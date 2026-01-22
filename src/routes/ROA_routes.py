from fastapi import APIRouter, UploadFile, File, HTTPException
from ROA.vectorstore_manager import load_vectorstore, add_chunks
from ROA.services import answer_question
from ROA.docling_utils import process_pdf
from schemas.ROA_schemas import ChatRequest, ChatResponse
import os
import shutil

ROA_router = APIRouter(prefix="/ROA", tags=["ROA"])

UPLOAD_DIR = (
    "/home/brain/projects/RAG para PDFs/"
    "RAG com OCR do Vini/"
    "ROA - RAG com OCR Academico/"
    "Documentos/uploads"
)

PDF_BASE = (
    "/home/brain/projects/RAG para PDFs/"
    "RAG com OCR do Vini/"
    "ROA - RAG com OCR Academico/"
    "Documentos/Documento sobre RAG-ENG.pdf"
)

@ROA_router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    answer = answer_question(req.question)
    return {"answer": answer}


@ROA_router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        chunks = process_pdf(file_path)
        add_chunks(chunks)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )

    return {
        "status": "success",
        "filename": file.filename,
        "message": "PDF added to knowledge base"
    }