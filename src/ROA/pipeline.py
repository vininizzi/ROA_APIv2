from langchain_community.chat_models import ChatOllama
from ROA.prompt_builder import build_prompt
from ROA.intent_classifier import classify_intent
from ROA.language import get_out_of_context_message
from ROA.llm_language import detect_language_llm
from ROA.vectorstore_manager import get_retriever

print("PIPELINE LOADED FROM:", __file__)

def run_pipeline(
    question: str,
    retriever=None,
    language: str | None = None
):
    print("=========== PIPELINE START ===========")
    print("Pergunta:", question)

    model = ChatOllama(
        model="gemma3:1b",
        temperature=0.2
    )

    # 🌍 Detecta idioma
    if language is None:
        language = detect_language_llm(question, model)

    print("Idioma detectado:", language)

    # 🎯 Classificação de intenção
    intent = classify_intent(question)
    print("Intenção:", intent)

    # 🔎 BUSCA NO VECTOR STORE
    print("=========== VECTOR STORE SEARCH ===========")

    if retriever is None:
        retriever = get_retriever(k=8)

    # ✅ CHAMADA CORRETA (nova API)
    retrieved = retriever.invoke(question)

    print(f"Chunks recuperados: {len(retrieved)}")

    for i, c in enumerate(retrieved):
        print(f"\n--- CHUNK {i+1} ---")
        print("Metadata:", c.metadata)
        print("Preview:")
        print(c.page_content[:400])

    if not retrieved:
        print("⚠️ Nenhum chunk encontrado no vector store")
        return get_out_of_context_message(language)

    # 🧩 Monta contexto
    context = "\n\n".join(
        f"==Fonte: {c.metadata.get('source', 'N/A')}==\n{c.page_content}"
        for c in retrieved[:8]
    )

    print("=========== CONTEXT FINAL ===========")
    #print(context[:1000])

    # 🧠 Prompt
    messages = build_prompt(context, question, intent, language)

    print("=========== PROMPT BUILT ===========")
    for role, msg in messages:
        print(f"[{role.upper()}]")
        print(msg[:500])

    # 🤖 Chamada LLM
    response = model.invoke(messages)

    print("=========== RAW LLM RESPONSE ===========")
    print(response.content)

    return response.content