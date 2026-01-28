from langchain_community.chat_models import ChatOllama

def detect_language_llm(question: str, model) -> str:
    print("### FUNÇÃO detect_language_llm EXECUTADA ###")
    prompt = f"""
Identify the language of the text below.
Reply with only the language name (for example: Portuguese, English, Spanish).
Do not add any extra text.

Text:
{question}
"""

    
    response = model.invoke(prompt)
    
    print("modelo chamado no detect")
    print(model)

    # Extrair texto
    if hasattr(response, "content"):
        raw_language = response.content.strip()
    else:
        raw_language = str(response).strip()

    print("DEBUG detect_language_llm:")
    print("  Pergunta:", question)
    print("  Resposta crua do LLM:", repr(raw_language))

    language = raw_language.lower()

    return language
