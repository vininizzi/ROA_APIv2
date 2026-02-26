import os
import logging
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger("ROA")

# ================= CONFIG =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FAISS_DIR = os.path.join(DATA_DIR, "faiss_index")

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ================= SINGLETONS =================

_vectorstore: Optional[FAISS] = None
_embeddings: Optional[HuggingFaceEmbeddings] = None


# ================= EMBEDDINGS =================

def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        logger.info("🧬 [EMBEDDINGS] Carregando HuggingFaceEmbeddings")
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings


# ================= LOAD / SAVE =================

def load_vectorstore() -> Optional[FAISS]:
    """
    Carrega o vectorstore do disco na inicialização.
    """
    global _vectorstore

    if _vectorstore is not None:
        logger.debug("📦 Vectorstore já carregado em memória")
        return _vectorstore

    if not os.path.exists(FAISS_DIR):
        logger.warning("📦 Nenhum FAISS index encontrado em disco")
        return None

    embeddings = get_embeddings()
    _vectorstore = FAISS.load_local(
        FAISS_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )

    logger.info("📦 Vectorstore carregado do disco")
    return _vectorstore


def _save_vectorstore():
    if _vectorstore is None:
        logger.error("❌ Tentativa de salvar vectorstore inexistente")
        return

    os.makedirs(DATA_DIR, exist_ok=True)
    _vectorstore.save_local(FAISS_DIR)
    logger.info("💾 Vectorstore salvo em disco")


# ================= API PÚBLICA =================

def get_vectorstore() -> FAISS:
    if _vectorstore is None:
        raise RuntimeError(
            "Vectorstore não inicializado. Nenhum documento ingerido ainda."
        )
    return _vectorstore


def add_chunks(chunks: List[Document]):
    """
    Cria ou adiciona chunks ao FAISS.
    """
    global _vectorstore

    if not chunks:
        raise ValueError("Lista de chunks vazia")

    logger.info(f"🧠 [VECTORSTORE] Recebidos {len(chunks)} chunks")

    embeddings = get_embeddings()

    if _vectorstore is None:
        logger.info("🧠 [VECTORSTORE] Criando novo FAISS index")
        _vectorstore = FAISS.from_documents(chunks, embeddings)
    else:
        logger.info("🧠 [VECTORSTORE] Adicionando documentos ao FAISS existente")
        _vectorstore.add_documents(chunks)

    _save_vectorstore()
    logger.info("✅ [VECTORSTORE] Indexação concluída")


# ================= RETRIEVER =================

def get_retriever(k: int = 8):
    """
    Retorna retriever com MMR (diversidade semântica).
    """
    vs = get_vectorstore()

    logger.info("🔍 [RETRIEVER] Usando MMR (diversidade ativada)")

    return vs.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": k,
            "fetch_k": 30,
            "lambda_mult": 0.7
        }
    )


def similarity_search(query: str, k: int = 4):
    """
    Busca direta por similaridade (sem MMR).
    """
    logger.info(f"🔍 [SEARCH] Query: {query}")
    vs = get_vectorstore()
    return vs.similarity_search(query, k=k)