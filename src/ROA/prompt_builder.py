"""
Módulo responsável pela construção do prompt final enviado ao modelo de
linguagem.

Este módulo consolida o contexto recuperado, a pergunta do usuário e a intenção
classificada, além de definir regras rígidas de comportamento, idioma da resposta
e restrições para evitar alucinações e extrapolações fora do documento fornecido.

Adições:
- Few-shot examples em English / Português / Español integrados ao system prompt
  para ancorar o padrão de idioma.
- Reforço do idioma também no bloco 'human' para aumentar a prioridade estatística.
"""

from typing import List, Tuple


def _system_text(intent: str, language: str = "English") -> str:
    """
    Texto base do system prompt.

    O idioma da resposta é um parâmetro do sistema e tem prioridade máxima,
    independentemente do idioma do contexto ou da pergunta do usuário.
    """

    system = (
        "You are an academic AI assistant specialized in document analysis. "
        "Your task is to answer questions based strictly on the information "
        "and meaning conveyed by the provided document context. "
        "Your answer must be clearly and directly related to the document content. "
        "Do NOT introduce external knowledge, definitions, or assumptions "
        "that are not supported by the document. "
        "If the document context does not contain sufficient information "
        "to reasonably answer the question, respond EXACTLY with: "
        "'Not found in the provided document.' "
        f"IMPORTANT LANGUAGE RULE: "
        f"You MUST answer in {language}. "
        f"The response language MUST be {language}, regardless of the language "
        "used in the context or the question."
    )

    if intent == "VERBATIM":
        system += (
            " Quote the relevant passage verbatim from the document. "
            "Do not paraphrase or alter the original wording."
        )

    elif intent == "DEFINITION":
        system += (
            " Provide a concise and formal definition derived from the document text. "
            "Paraphrasing is allowed as long as the meaning is preserved."
        )

    elif intent == "LOCATION":
        system += (
            " Indicate where the information appears in the document, "
            "such as the section, heading, or page, if this information is available."
        )

    elif intent == "CONTENT":
        system += (
            " Summarize the main topics and structure of the document. "
            "Focus on what the document covers, not on external explanations."
        )

    return system



def _human_text(context: str, question: str, language: str) -> str:
    few_shots = {
        "English": (
            "Example:\n"
            "Context:\n"
            "Retrieval-Augmented Generation (RAG) is a method that combines "
            "information retrieval with text generation models to improve "
            "the quality of generated answers.\n\n"
            "Question:\n"
            "What is RAG?\n\n"
            "Answer:\n"
            "RAG is a method that combines information retrieval with text generation "
            "models to improve the quality of generated answers.\n\n"
        ),
        "Portuguese": (
            "Exemplo:\n"
            "Contexto:\n"
            "Retrieval-Augmented Generation (RAG) é um método que combina "
            "recuperação de informação com modelos de geração de texto "
            "para melhorar a qualidade das respostas geradas.\n\n"
            "Pergunta:\n"
            "O que é RAG?\n\n"
            "Resposta:\n"
            "RAG é um método que combina recuperação de informação com modelos "
            "de geração de texto para melhorar a qualidade das respostas geradas.\n\n"
        ),
        "Spanish": (
            "Ejemplo:\n"
            "Contexto:\n"
            "Retrieval-Augmented Generation (RAG) es un método que combina "
            "la recuperación de información con modelos de generación de texto "
            "para mejorar la calidad de las respuestas generadas.\n\n"
            "Pregunta:\n"
            "¿Qué es RAG?\n\n"
            "Respuesta:\n"
            "RAG es un método que combina la recuperación de información con modelos "
            "de generación de texto para mejorar la calidad de las respuestas generadas.\n\n"
        )
    }

    return (
        few_shots.get(language, "")
        + f"Context:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        f"IMPORTANT: Answer in {language}.\n"
        "Answer:"
    )



def build_prompt(
    context: str,
    question: str,
    intent: str,
    language: str = "English",
    mode: str = "chat"
):
    """
    Constrói o prompt final.

    Args:
        context: Texto de contexto (documento ou chunks recuperados).
        question: Pergunta do usuário.
        intent: Intenção classificada (e.g. 'VERBATIM', 'DEFINITION', 'LOCATION', 'CONTENT').
        language: Idioma da resposta (ex: 'Portuguese', 'English', 'Spanish').
        mode: 'chat' retorna List[Tuple[str, str]]
              'text' retorna uma string única.

    Returns:
        List[Tuple[str, str]] se mode == 'chat'
        str se mode == 'text'
    """

    system = _system_text(intent, language)
    human = _human_text(context, question, language)

    if mode == "chat":
        # Formato ideal para ChatOllama / LangChain
        return [
            ("system", system),
            ("human", human)
        ]

    elif mode == "text":
        # Modo texto puro (menos robusto, mas funcional)
        if intent == "VERBATIM":
            instruction = "Quote the answer verbatim from the context."
        elif intent == "DEFINITION":
            instruction = "Provide a concise definition based strictly on the context."
        elif intent == "LOCATION":
            instruction = "Indicate where the information appears in the document."
        else:
            instruction = "Answer strictly using the provided context."

        return (
            "You are an academic AI text analysis assistant.\n"
            f"IMPORTANT LANGUAGE RULE:\n"
            f"You MUST respond in {language}.\n"
            f"The response language MUST be {language}.\n"
            "Do not change the response language under any circumstances.\n\n"
            f"Context:\n{context}\n\n"
            f"Instruction:\n{instruction}\n\n"
            f"Question:\n{question}\n\n"
            "Answer:"
        )

    else:
        raise ValueError("mode must be 'chat' or 'text'")
