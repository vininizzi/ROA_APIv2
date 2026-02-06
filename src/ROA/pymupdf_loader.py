import fitz  # PyMuPDF
from langchain_core.documents import Document
from pathlib import Path
import hashlib
import re
from datetime import datetime
import os

def generate_doc_id(file_path: str) -> str:
    name = Path(file_path).stem.lower().replace(" ", "_")
    hash_part = hashlib.md5(file_path.encode()).hexdigest()[:6]
    return f"{name}_{hash_part}"

def parse_pdf_date(date_str: str | None):
    """
    Converte datas do padrão PDF: D:YYYYMMDDHHmmSS
    """
    if not date_str:
        return None

    try:
        date_str = date_str.replace("D:", "")
        return datetime.strptime(date_str[:14], "%Y%m%d%H%M%S")
    except Exception:
        return None


def process_pdf(file_path: str):
    pdf = fitz.open(file_path)
    documents = []

    doc_id = generate_doc_id(file_path)
    total_pages = pdf.page_count

    for page_index, page in enumerate(pdf):
        text = page.get_text("text").strip()
        if not text:
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "chunk_id": f"{doc_id}_p{page_index + 1}",
                    "doc_id": doc_id,
                    "page": page_index + 1,
                    "total_pages": total_pages,
                    "source": os.path.basename(file_path),
                }
            )
        )

    if not documents:
        raise ValueError("Nenhum texto extraído do PDF.")

    return documents, doc_id

