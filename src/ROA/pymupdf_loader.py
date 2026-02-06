import fitz  # PyMuPDF
from langchain_core.documents import Document
from pathlib import Path
import hashlib
import re
from datetime import datetime
import os

from utils.date_conversion import parse_pdf_date_from_spec

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

    # 🔹 Metadados brutos do PDF
    metadata_dict = pdf.metadata or {}

    # 🔹 Mapeamento padronizado (nível documento)
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
        "creation_date": parse_pdf_date_from_spec(metadata_dict.get("creationDate")),
        "modification_date": parse_pdf_date_from_spec(metadata_dict.get("modDate")),
        "creation_date_raw": metadata_dict.get("creationDate"),
        "modification_date_raw": metadata_dict.get("modDate"),
        "source": os.path.basename(file_path),
        "file_path": file_path,
        "total_pages": total_pages,
    }

    # 🔹 Geração dos chunks por página
    for page_index, page in enumerate(pdf):
        text = page.get_text("text").strip()
        if not text:
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    **metadata_mapped,               # ✅ metadados globais
                    "chunk_id": f"{doc_id}_p{page_index + 1}",
                    "page": page_index + 1,          # ✅ metadado específico do chunk
                }
            )
        )

    pdf.close()
    return documents, doc_id

