import os
from langchain_docling import DoclingLoader
from ROA.chunking import build_chunks
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS

# Caminho base do projeto (TEMPORÁRIO – para acelerar testes)
PROJECT_ROOT = (
    "/home/brain/projects/RAG para PDFs/"
    "RAG com OCR do Vini/"
    "ROA - RAG com OCR Academico"
)

DOCUMENTS_DIR = os.path.join(PROJECT_ROOT, "Documentos")


def process_pdf(pdf_name: str):
    """
    Carrega um PDF e retorna apenas os chunks prontos para indexação.
    """
    pdf_path = os.path.join(DOCUMENTS_DIR, pdf_name)

    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

    loader = DoclingLoader(file_path=[pdf_path], export_type="doc_chunks")
    documents = loader.load()

    if not documents:
        raise ValueError("Falha na extração do documento com Docling.")

    text = "\n\n".join(doc.page_content for doc in documents)
    chunks = build_chunks(text, pdf_name)

    print(f"Documento processado! {len(chunks)} chunks criados.")

    return chunks
