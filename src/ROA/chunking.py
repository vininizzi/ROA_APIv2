"""
Módulo responsável pela segmentação do texto de entrada em unidades menores
(chunks) semanticamente coerentes.

A segmentação é baseada em parágrafos lógicos do documento, preservando
títulos, subtítulos e blocos definicionais completos, sem perda de conteúdo.
"""

from langchain_core.documents import Document


def build_chunks(text: str, source: str):
    # Normalização mínima para corrigir hifenização e quebras artificiais
    text = text.replace("-\n", "")
    
    # Divide o texto em parágrafos reais
    paragraphs = [
        p.strip()
        for p in text.split("\n\n")
        if p.strip()
    ]

    enriched = []
    for i, p in enumerate(paragraphs):
        enriched.append(
            Document(
                page_content=p,
                metadata={
                    "source": source,
                    "chunk_id": i + 1
                }
            )
        )

    return enriched
