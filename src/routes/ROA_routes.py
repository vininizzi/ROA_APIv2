from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ROA.vectorstore_manager import add_chunks
from services.ROA_services import answer_question, create_document_metadata_service, delete_document_service
from ROA.pymupdf_loader import process_pdf
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

@ROA_router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    answer = answer_question(req.question)
    return {"answer": answer}

@ROA_router.post("/upload")
def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):

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

        logger.info("📄 [UPLOAD] Iniciando processamento do PDF")
        chunks, document_index = process_pdf(file_path)

        doc_id = chunks[0].metadata.get("doc_id", str(uuid.uuid4()))
        add_chunks(chunks)
        logger.info(f"✅ [INGEST] FAISS atualizado com {len(chunks)} chunks")

        # Mapeando metadados do PDF para o modelo SQLAlchemy
        metadata_dict = chunks[0].metadata  # assumindo que os metadados estão no primeiro chunk
        metadata_mapped = {
            "doc_id": doc_id,
            "producer": metadata_dict.get("producer"),
            "creator": metadata_dict.get("creator"),
            "title": metadata_dict.get("title"),
            "author": metadata_dict.get("author"),
            "subject": metadata_dict.get("subject"),
            "keywords": metadata_dict.get("keywords"),
            "format": metadata_dict.get("format"),
            "trapped": metadata_dict.get("trapped"),
            "creation_date": metadata_dict.get("creation_date"),
            "modification_date": metadata_dict.get("moddate"),
            "creation_date_raw": metadata_dict.get("creationdate"),
            "modification_date_raw": metadata_dict.get("moddate"),
            "source": metadata_dict.get("source", "ROA_UPLOAD"),
            "file_path": file_path,
            "total_pages": metadata_dict.get("total_pages", len(chunks)),
        }

        # Cria o registro no banco
        metadata_record = create_document_metadata_service(db, metadata_mapped)

        logger.info(f"✅ [UPLOAD] Ingestão e salvamento no DB concluídos | doc_id={doc_id}")

        return {
            "status": "success",
            "filename": file.filename,
            "doc_id": doc_id,
            "chunks": len(chunks),
            "metadata_id": metadata_record.id
        }

    except Exception as e:
        logger.exception("❌ [UPLOAD] Erro durante upload/ingestão")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@ROA_router.delete("/delete/{doc_id}")
def delete(doc_id: str, db: Session = Depends(get_db)):
    delete_document_service(db, doc_id)
