import os
import pickle
import logging
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger("ROA")

# ================= CONFIG =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
VECTORSTORE_PATH = os.path.join(DATA_DIR, "faiss_store.pkl")

# ================= SINGLETON =================

_vectorstore: Optional[FAISS] = None

# ================= EMBEDDINGS =================

from langchain_community.embeddings import HuggingFaceEmbeddings

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        print("🧬 [EMBEDDINGS] HuggingFace local")
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings
# ================= LOAD / SAVE =================

def load_vectorstore() -> Optional[FAISS]:
    """
    Carrega o vectorstore do disco (startup).
    """
    global _vectorstore

    if _vectorstore is not None:
        logger.debug("📦 Vectorstore já carregado em memória")
        return _vectorstore

    if not os.path.exists(VECTORSTORE_PATH):
        logger.warning("📦 Nenhum vectorstore encontrado em disco")
        return None

    with open(VECTORSTORE_PATH, "rb") as f:
        _vectorstore = pickle.load(f)

    logger.info("📦 Vectorstore carregado do disco")
    return _vectorstore


def _save_vectorstore():
    if _vectorstore is None:
        logger.error("❌ Tentativa de salvar vectorstore inexistente")
        return

    os.makedirs(DATA_DIR, exist_ok=True)

    with open(VECTORSTORE_PATH, "wb") as f:
        pickle.dump(_vectorstore, f)

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

    logger.info(f"✅ [VECTORSTORE] {len(chunks)} chunks processados")


def similarity_search(query: str, k: int = 4):
    """
    Busca semântica (RAG).
    """
    logger.info(f"🔍 [SEARCH] Query: {query}")
    vs = get_vectorstore()
    return vs.similarity_search(query, k=k)
