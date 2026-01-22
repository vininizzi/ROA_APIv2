import os
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# ===== CONFIGURAÇÃO =====

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")
INDEX_NAME = "roa_faiss_index"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ===== SINGLETONS =====

_vectorstore = None
_embeddings = None


# ===== FUNÇÕES INTERNAS =====

def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings


def _index_exists() -> bool:
    return os.path.exists(os.path.join(VECTORSTORE_DIR, INDEX_NAME))


# ===== API PÚBLICA =====

def load_vectorstore():
    """
    Carrega o índice FAISS persistido ou cria um novo vazio.
    Deve ser chamado UMA vez no startup.
    """
    global _vectorstore

    embeddings = _get_embeddings()
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)

    if _index_exists():
        print("Carregando índice FAISS existente...")
        _vectorstore = FAISS.load_local(
            VECTORSTORE_DIR,
            embeddings,
            index_name=INDEX_NAME,
            allow_dangerous_deserialization=True,
        )
    else:
        print("Nenhum índice FAISS encontrado. Será criado na primeira ingestão.")
        _vectorstore = None


    return _vectorstore


def get_vectorstore():
    if _vectorstore is None:
        raise RuntimeError(
            "VectorStore ainda não inicializado. "
            "Nenhum documento foi ingerido."
        )
    return _vectorstore



def add_chunks(chunks):
    global _vectorstore

    embeddings = _get_embeddings()

    if _vectorstore is None:
        print("Criando índice FAISS com primeiros chunks...")
        _vectorstore = FAISS.from_documents(chunks, embeddings)
    else:
        _vectorstore.add_documents(chunks)

    _vectorstore.save_local(VECTORSTORE_DIR, INDEX_NAME)
    print(f"{len(chunks)} chunks adicionados ao índice.")



def similarity_search(query: str, k: int = 4):
    """
    Busca semântica no índice.
    """
    vs = get_vectorstore()
    return vs.similarity_search(query, k=k)
