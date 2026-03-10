from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ROA.vectorstore_manager import add_chunks
from services.ROA_services import answer_question, create_document_metadata_service, delete_document_service
#from ROA.pymupdf_loader import process_pdf
from ROA.docling_utils import process_pdf
from ROA.chunking import build_chunks
from schemas.ROA_schemas import ChatRequest, ChatResponse
from sqlalchemy.orm import Session
from database import get_db
import os
import shutil
import logging
import uuid

logger = logging.getLogger("ROA")

ROA_router = APIRouter(prefix="/ROA", tags=["ROA"])

UPLOAD_DIR = (
    "/home/brain/projects/RAG para PDFs/"
    "RAG com OCR do Vini/"
    "ROA - RAG com OCR Academico/"
    "Documentos/uploads"
)

from core.security import get_current_user
from models.users_model import User

@ROA_router.post("/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest, 
    db: Session = Depends(get_db)
):
    # Bypass de login para testes
    user_id = "vini_mock_id"
    
    result = answer_question(
        db=db, 
        question=req.question, 
        user_id=user_id, 
        conversation_id=req.conversation_id
    )
    return result

@ROA_router.get("/history/", response_model=list)
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from models.chat_history_model import Conversation
    user_id = current_user.id
    print(user_id)
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
    print(conversations)
    return conversations

@ROA_router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):

    logger.info(f"📥 [UPLOAD] Arquivo recebido: {file.filename}")

    if not file.filename.lower().endswith(".pdf"):
        logger.warning("❌ [UPLOAD] Arquivo não é PDF")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        logger.info(f"💾 [UPLOAD] Salvando arquivo em {file_path}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info("📄 [UPLOAD] Iniciando processamento do PDF (Docling)")

        # ✅ PASSA O CAMINHO COMPLETO
        text = process_pdf(file_path)

        logger.info("✂️ [UPLOAD] Iniciando chunking")

        chunks = build_chunks(
            text=text,
            source=file.filename,
            global_metadata=None
        )

        logger.info(f"🧠 [UPLOAD] Indexando {len(chunks)} chunks no vector store")

        add_chunks(chunks)

        logger.info("✅ [UPLOAD] Documento ingerido com sucesso")

        return {
            "status": "success",
            "filename": file.filename,
            "chunks": len(chunks)
        }

    except Exception as e:
        logger.exception("❌ [UPLOAD] Erro durante upload/ingestão")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@ROA_router.delete("/delete/{doc_id}")
def delete(doc_id: str, db: Session = Depends(get_db)):
    delete_document_service(db, doc_id)
