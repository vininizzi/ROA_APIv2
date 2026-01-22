from langdetect import detect, LangDetectException, detect_langs

def detect_language(text: str) -> str:
    try:
        langs = detect_langs(text)

        print("\n=== LANGUAGE DETECTION DEBUG ===")
        print(f"Texto recebido: {text}")
        print(f"Probabilidades: {langs}")

        lang = langs[0].lang
        print(f"Idioma escolhido: {lang}")
        print("================================")

        return lang

    except LangDetectException as e:
        print("\n=== LANGUAGE DETECTION ERROR ===")
        print(f"Erro: {e}")
        print("Fallback para 'en'")
        print("================================")

        return "en"

LANG_MAP = {
    "pt": "Portuguese",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian"
}

def normalize_language(lang_code: str) -> str:
    return LANG_MAP.get(lang_code, "English")

OUT_OF_CONTEXT_MESSAGES = {
    "English": "Not found in the provided document.",
    "Portuguese": "Não encontrado no documento fornecido.",
    "Spanish": "No se encontró en el documento proporcionado.",
    "French": "Non trouvé dans le document fourni.",
    "Italian": "Non trovato nel documento fornito.",
    "German": "Im bereitgestellten Dokument nicht gefunden."
}

def get_out_of_context_message(language: str) -> str:
    return OUT_OF_CONTEXT_MESSAGES.get(
        language,
        OUT_OF_CONTEXT_MESSAGES["English"]
    )