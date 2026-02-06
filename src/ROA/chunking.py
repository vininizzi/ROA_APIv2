"""
Módulo responsável pela segmentação do texto em chunks semanticamente coerentes
para indexação em sistemas RAG acadêmicos.

Este chunker:
- Preserva parágrafos lógicos
- Controla tamanho mínimo e máximo
- Evita chunks muito pequenos ou muito grandes
- Anexa metadados estruturais úteis para recuperação e auditoria
"""

from langchain_core.documents import Document
from typing import List, Dict


def build_chunks(
    text: str,
    source: str,
    global_metadata: Dict | None = None,
    min_chars: int = 300,
    max_chars: int = 1200,
) -> List[Document]:
    """
    Constrói chunks a partir de texto linearizado.

    Args:
        text: Texto completo do documento.
        source: Nome ou identificador do documento.
        global_metadata: Metadados globais do documento (opcional).
        min_chars: Tamanho mínimo de um chunk.
        max_chars: Tamanho máximo de um chunk.

    Returns:
        Lista de Documents prontos para indexação.
    """

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

    # -------------------------------
    # 2️⃣ Agrupamento semântico
    # -------------------------------
    for p in paragraphs:
        if len(buffer) + len(p) <= max_chars:
            buffer += ("\n\n" + p) if buffer else p
        else:
            if len(buffer) >= min_chars:
                chunks.append(
                    _make_chunk(
                        buffer,
                        source,
                        chunk_id,
                        global_metadata
                    )
                )
                chunk_id += 1
                buffer = p
            else:
                # força agregação se chunk ficou pequeno
                buffer += ("\n\n" + p)

    # -------------------------------
    # 3️⃣ Último chunk
    # -------------------------------
    if buffer.strip():
        chunks.append(
            _make_chunk(
                buffer,
                source,
                chunk_id,
                global_metadata
            )
        )

    return chunks


def _make_chunk(
    content: str,
    source: str,
    chunk_id: int,
    global_metadata: Dict | None
) -> Document:
    """
    Cria um Document com metadados estruturados.
    """

    metadata = {
        "source": source,
        "chunk_id": chunk_id,
        "chunk_size": len(content),
        "chunk_type": "text",
    }

    if global_metadata:
        metadata["document_metadata"] = global_metadata

    return Document(
        page_content=content,
        metadata=metadata
    )
