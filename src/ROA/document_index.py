import fitz
from pathlib import Path
import hashlib

def generate_doc_id(file_path: str) -> str:
    name = Path(file_path).stem.lower().replace(" ", "_")
    hash_part = hashlib.md5(file_path.encode()).hexdigest()[:6]
    return f"{name}_{hash_part}"

def build_document_index(file_path: str) -> dict:
    pdf = fitz.open(file_path)
    meta = pdf.metadata

    doc_id = generate_doc_id(file_path)

    document_record = {
        "doc_id": doc_id,
        "title": meta.get("title") or Path(file_path).stem,
        "author": meta.get("author"),
        "subject": meta.get("subject"),
        "keywords": meta.get("keywords"),
        "total_pages": pdf.page_count,
        "source": file_path,
        "summary": None,
        "topics": [],
        "embedding": None,
    }

    return document_record
