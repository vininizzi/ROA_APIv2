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
    Texto base do system prompt refinado para ser estritamente acadêmico e prioritário em documentos.
    """

    system = (
        "You are a strict academic AI assistant specialized in education and document analysis. "
        "Your mission is to help students learn and understand academic materials.\n\n"
        "RESPONSE STRUCTURE STRICT RULES:\n"
        "You MUST respond separating the explanation from the code using EXACTLY these tags:\n\n"
        "[EXPLANATION]:\n"
        "Your academic explanation here (leave empty lines after this).\n\n"
        "[CODE]:\n"
        "```(your exact language identifier, e.g. python, cpp, javascript)\n"
        "Your code here ALWAYS wrapped in triple backticks! Do not write code without these backticks!\n"
        "```\n\n"
        "[SOURCE]:\n"
        "Mention if the info is from the document or general knowledge.\n\n"
        "RULES:\n"
        "1. **Academic Only**: Answer only academic questions.\n"
        "2. **Document Priority**: Use provided context as primary truth.\n"
        "3. **Code Formatting**: NEVER merge explanation and code on the same paragraph. ALWAYS surround code with ``` .\n"
        f"You MUST answer in {language}."
    )

    if intent == "VERBATIM":
        system += " Quote relevant passages exactly."
    elif intent == "DEFINITION":
        system += " Provide formal definitions."
    # Adicionando suporte a intent de estudo se necessário futuramente
    return system


def _human_text(context: str, question: str, language: str) -> str:
    few_shots = {
        "English": (
            "Context: (Academic material)\n"
            "Question: (Student question)\n"
            "Answer: (Helpful academic response)\n\n"
        ),
        "Portuguese": (
            "Contexto: (Material acadêmico)\n"
            "Pergunta: (Pergunta do aluno)\n"
            "Resposta: (Resposta acadêmica útil)\n\n"
        ),
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
    history: list = None,
    mode: str = "chat"
):
    """
    Constrói o prompt final.
    """

    system = _system_text(intent, language)
    human = _human_text(context, question, language)

    if mode == "chat":
        messages = [("system", system)]
        
        # Adicionar histórico se houver
        if history:
            for role, content in history:
                messages.append((role, content))
        
        messages.append(("human", human))
        return messages
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
