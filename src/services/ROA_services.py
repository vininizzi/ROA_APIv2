# services/ROA_services.py

import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging
from sqlalchemy.sql import func

logger = logging.getLogger("ROA")
# =========================
# ROA / RAG / Question Answering
# =========================
from ROA.pipeline import run_pipeline
from ROA.llm_language import detect_language_llm
from ROA.vectorstore_manager import get_vectorstore

def clean_pdf_text(text: str) -> str:
    """
    Remove quebras de linha e hífens de PDFs, mantendo parágrafos legíveis.
    """
    import re
    # Remove hífen seguido de quebra de linha (palavra dividida)
    text = re.sub(r'-\n', '', text)
    # Substitui quebras de linha restantes por espaço
    text = re.sub(r'\n', ' ', text)
    # Remove múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


from models.chat_history_model import Conversation, Message

def answer_question(db: Session, question: str, user_id: str, conversation_id: str = None) -> dict:
    # 1. Obter ou criar conversação
    conversation_id = conversation_id
    chat_history = []
    
    try:
        if conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
            if not conversation:
                # Se não achou, vamos criar uma nova (vini_mock_id case)
                conversation = Conversation(user_id=user_id, title=question[:50])
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
                conversation_id = conversation.id
        else:
            conversation = Conversation(user_id=user_id, title=question[:50])
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            conversation_id = conversation.id

        # 2. Resgatar histórico
        history = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(10).all()
        
        history = history[::-1]
        for msg in history:
            chat_history.append((msg.role, msg.content))
            
    except Exception as e:
        logger.error(f"⚠️ Erro ao acessar histórico no banco (provavelmente user {user_id} não existe): {e}")
        # Se falhou o banco, seguimos sem histórico para não dar 500
        conversation_id = conversation_id or "temp_id"

    # 4. Executar o pipeline
    vector_store = get_vectorstore()
    result = run_pipeline(
        question=question,
        retriever=vector_store.as_retriever(search_kwargs={"k": 8}),
        language=None,
        history=chat_history
    )

    answer = clean_pdf_text(result)

    # 5. Salvar mensagens no banco (opcional/best effort)
    try:
        if conversation_id != "temp_id":
            user_msg = Message(conversation_id=conversation_id, role="user", content=question)
            assistant_msg = Message(conversation_id=conversation_id, role="assistant", content=answer)
            db.add(user_msg)
            db.add(assistant_msg)
            db.commit()
    except Exception as e:
        logger.error(f"⚠️ Erro ao salvar mensagem no banco: {e}")

    return {
        "answer": answer, 
        "conversation_id": conversation_id,
        "history_count": len(chat_history)
    }


# =========================
# CRUD de Metadados
# =========================
from database import get_db
from models.metadata_model import DocumentMetadata  # modelo SQLAlchemy para metadados

def create_document_metadata_service(db: Session, metadata: dict):
    """
    Insere um registro de metadados de documento no banco.
    """
    db_metadata = DocumentMetadata(
        id=str(uuid.uuid4()),
        doc_id=metadata.get("doc_id") or str(uuid.uuid4()),
        producer=metadata.get("producer"),
        creator=metadata.get("creator"),
        creation_date=metadata.get("creation_date"),
        source=metadata.get("source"),
        file_path=metadata.get("file_path"),
        total_pages=metadata.get("total_pages"),
        format=metadata.get("format"),
        title=metadata.get("title"),
        author=metadata.get("author"),
        subject=metadata.get("subject"),
        keywords=metadata.get("keywords"),
        modification_date=metadata.get("modification_date"),
        trapped=metadata.get("trapped"),
        #page=metadata.get("page", 0),
        #created_at=func.now(),
        #updated_at=func.now()
    )
    db.add(db_metadata)
    db.commit()
    db.refresh(db_metadata)
    return db_metadata


def get_all_documents_service(db: Session, page: int = 1, limit: int = 10):
    """
    Retorna todos os documentos paginados
    """
    offset = (page - 1) * limit
    total_count = db.query(DocumentMetadata).count()
    documents = db.query(DocumentMetadata).offset(offset).limit(limit).all()

    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "documents": documents
    }


def get_document_by_id_service(db: Session, doc_id: str):
    """
    Retorna documento pelo ID
    """
    doc = db.query(DocumentMetadata).filter(DocumentMetadata.id == doc_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {doc_id} not found"
        )
    return doc


def update_document_metadata_service(db: Session, doc_id: str, update_data: dict):
    """
    Atualiza metadados de documento
    """
    doc = get_document_by_id_service(db, doc_id)

    for key, value in update_data.items():
        if hasattr(doc, key):
            setattr(doc, key, value)

    db.commit()
    db.refresh(doc)
    return doc


def delete_document_service(db: Session, doc_id: str):
    """
    Deleta documento (hard delete)
    """
    doc = get_document_by_id_service(db, doc_id)
    db.delete(doc)
    db.commit()
    return {"status": "deleted", "doc_id": doc_id}
    