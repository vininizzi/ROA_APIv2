from docling.document_converter import DocumentConverter
import os


def process_pdf(pdf_path: str) -> str:
    """
    Executa OCR e extração de texto com Docling.
    Recebe o CAMINHO COMPLETO do PDF.
    Retorna APENAS o texto.
    """

    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

    print("=========== DOCLING ==========")
    print(f"Processando arquivo: {pdf_path}")

    converter = DocumentConverter()
    result = converter.convert(pdf_path)

    if result.status != "success":
        raise RuntimeError(f"Falha na conversão: {result.errors}")

    doc = result.document
    text = doc.export_to_text()

    # ======================================
    # DEBUG DESATIVADO (preview curto)
    # ======================================
    # print("=========== OCR RESULT ==========")
    # print(text[:1000])
    # print("Tamanho do texto:", len(text))

    # ======================================
    # DEBUG COMPLETO (PRINT TOTAL)
    # ⚠️ Use só para arquivos pequenos
    # ======================================
    #print("=========== OCR FULL TEXT ==========")
    #print(text)

    # ======================================
    # SALVAR TEXTO BRUTO EM ARQUIVO .txt
    # ======================================
    # txt_path = pdf_path + ".ocr.txt"
    # with open(txt_path, "w", encoding="utf-8") as f:
    #     f.write(text)

    # print(f"📄 Texto OCR salvo em: {txt_path}")
    # print("Tamanho total do texto:", len(text))

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Texto extraído está vazio")

    return text