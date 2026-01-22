from ROA.pipeline import run_pipeline
from ROA.language import detect_language, normalize_language
from ROA.vectorstore_manager import similarity_search, get_vectorstore


def answer_question(question: str) -> str:
    """
    Responde uma pergunta usando a base de conhecimento persistente.

    A função:
    - Detecta e normaliza o idioma
    - Recupera documentos relevantes via VectorStore
    - Executa o pipeline RAG
    """

    # 1. Detecta e normaliza idioma
    lang_code = detect_language(question)
    language = normalize_language(lang_code)

    # 2. Obtém o VectorStore já carregado
    vector_store = get_vectorstore()

    # 3. Executa pipeline RAG
    answer = run_pipeline(
        question=question,
        retriever=vector_store.as_retriever(search_kwargs={"k": 8}),
        language=language
    )

    return answer
