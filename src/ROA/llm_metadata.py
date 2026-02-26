import json

def extract_metadata_with_llm(text: str, llm) -> dict:
    print("=========== adiciona os metadados ===========")
    prompt = f"""
Extraia os seguintes metadados do texto abaixo.
Retorne APENAS um JSON válido.

Campos:
- title
- author
- year
- document_type
- area
- summary
- keywords (lista)

Se algum campo não existir, use null.

Texto:
{text[:8000]}
"""

    response = llm.invoke(prompt)

    try:
        metadata = json.loads(response)
    except json.JSONDecodeError:
        raise ValueError("LLM não retornou JSON válido")

    return metadata