"""
Módulo responsável pela classificação da intenção da pergunta do usuário.

A intenção determina o modo de resposta do sistema (por exemplo, resposta
direta, localização de trecho, resumo ou explicação), influenciando tanto a
seleção de contexto quanto a construção do prompt enviado ao modelo de linguagem.
"""

import re

def count_matches(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text))


def classify_intent(question: str) -> str:
    q = question.lower()

    VERBATIM_PATTERNS = r"quote|verbatim|exact|citar|transcrev|trecho literal|citação direta"
    DEFINITION_PATTERNS = r"define|definition|what is|o que é|significa|conceito|definição"
    LOCATION_PATTERNS = r"where|which section|onde|em qual parte|capítulo|seção|página"
    CONTENT_PATTERNS = r"conteúdo|temas|tópicos|assuntos|do que trata|sobre o que é|estrutura|organização|panorama|visão geral|índice|sumário"



    scores = {
        "VERBATIM": count_matches(VERBATIM_PATTERNS, q),
        "DEFINITION": count_matches(DEFINITION_PATTERNS, q),
        "LOCATION": count_matches(LOCATION_PATTERNS, q),
        "CONTENT" : count_matches(CONTENT_PATTERNS, q)
    }

    best_intent = max(scores, key=scores.get)

    if scores[best_intent] == 0:
        return "GENERAL"

    return best_intent

