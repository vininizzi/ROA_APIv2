"""
Pipeline RAG simplificado: recebe um retriever já pronto e gera a resposta via LLM.
"""

from langchain_community.chat_models import ChatOllama
from ROA.prompt_builder import build_prompt
from ROA.intent_classifier import classify_intent
from ROA.language import get_out_of_context_message
from ROA.llm_language import detect_language_llm


print("PIPELINE LOADED FROM:", __file__)

def run_pipeline(
    question: str,
    retriever,
    language: str | None = None
):

    model = ChatOllama(
        model="gemma3:1b",
        temperature=0.2
    )
    # Detecta idioma se não informado
    '''
    if language is None:
        lang_code = detect_language(question)
        language = normalize_language(lang_code)
    '''
    #detecta o idioma usando llm se n for informado
    if language is None:
        language = detect_language_llm(question, model)
        
    # Classificação de intenção (para controle do prompt)
    intent = classify_intent(question)

    # Recuperação semântica
    retrieved = retriever.invoke(question)

    if not retrieved:
        return get_out_of_context_message(language)

    # Monta contexto final com os primeiros 8 chunks
    context = "\n\n".join(
        f"==Fonte: {c.metadata.get('source', 'N/A')} | "
        f"Página: {c.metadata.get('page', 'N/A')}==\n"
        f"{c.page_content}"
        for c in retrieved[:8]
    )


    # Construção do prompt
    messages = build_prompt(context, question, intent, language)

    # Chamada do modelo LLM
    model = ChatOllama(
        model="gemma3:1b",
        temperature=0.2
    )

    response = model.invoke(messages)
    return response.content
