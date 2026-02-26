from langchain_core.documents import Document
from typing import List, Dict
import hashlib


def build_chunks(
    text: str,
    source: str,
    global_metadata: Dict | None = None,
    min_chars: int = 300,
    max_chars: int = 1200,
) -> List[Document]:

    # -------------------------------
    # 1️⃣ Normalização leve
    # -------------------------------
    text = text.replace("-\n", "")
    text = text.replace("\n \n", "\n\n")

    paragraphs = [
        p.strip()
        for p in text.split("\n\n")
        if p.strip()
    ]

    chunks: List[Document] = []
    buffer = ""
    chunk_id = 1

    seen_hashes = set()  # 🔹 CONTROLE DE DUPLICAÇÃO

    # -------------------------------
    # 2️⃣ Agrupamento semântico
    # -------------------------------
    for p in paragraphs:
        if len(buffer) + len(p) <= max_chars:
            buffer += ("\n\n" + p) if buffer else p
        else:
            if len(buffer) >= min_chars:
                _try_add_chunk(
                    buffer,
                    source,
                    chunk_id,
                    global_metadata,
                    chunks,
                    seen_hashes
                )
                chunk_id += 1
                buffer = p
            else:
                buffer += ("\n\n" + p)

    # -------------------------------
    # 3️⃣ Último chunk
    # -------------------------------
    if buffer.strip():
        _try_add_chunk(
            buffer,
            source,
            chunk_id,
            global_metadata,
            chunks,
            seen_hashes
        )

    return chunks


def _try_add_chunk(
    content: str,
    source: str,
    chunk_id: int,
    global_metadata: Dict | None,
    chunks: List[Document],
    seen_hashes: set,
):
    normalized = " ".join(content.split())
    h = hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    if h in seen_hashes:
        return  # 🔴 IGNORA CHUNK DUPLICADO

    seen_hashes.add(h)

    metadata = {
        "source": source,
        "chunk_id": chunk_id,
        "chunk_size": len(content),
        "chunk_type": "text",
    }

    if global_metadata:
        metadata["document_metadata"] = global_metadata

    chunks.append(
        Document(page_content=content, metadata=metadata)
    )