import os
# 🔥 FORÇA CPU — mata o problema de vez
#os.environ["CUDA_VISIBLE_DEVICES"] = ""
#os.environ["OMP_NUM_THREADS"] = "1"
#os.environ["MKL_NUM_THREADS"] = "1"

from docling.document_converter import DocumentConverter

print("==== Debug 1 ====")
print("PID:", os.getpid())

# ⚠️ Ideal mover depois para config/env
PROJECT_ROOT = (
    "/home/brain/projects/RAG para PDFs/"
    "RAG com OCR do Vini/"
    "ROA - RAG com OCR Academico"
)

DOCUMENTS_DIR = os.path.join(PROJECT_ROOT, "Documentos")


def process_pdf(pdf_name: str):
    """
    Executa APENAS OCR e extração estrutural com Docling.
    Retorna texto linearizado + metadados do documento.
    NÃO faz chunking.
    NÃO faz indexação.
    """

    pdf_path = os.path.join(DOCUMENTS_DIR, pdf_name)

    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

    # =========================================================
    # 1️⃣ Conversão com Docling
    # =========================================================
    print("==== Debug 2 ====")
    print("PID:", os.getpid())
    
    converter = DocumentConverter()
    result = converter.convert(pdf_path)

    if result.status != "success":
        raise RuntimeError(
            f"Falha na conversão do documento: {result.errors}"
        )

    doc = result.document

    # =========================================================
    # 2️⃣ Metadados NATIVOS (Docling)
    # =========================================================
    #num_pages = doc.num_pages() if callable(doc.num_pages) else doc.num_pages

    native_metadata: dict[str, str] = {
        "doc_name": doc.name,
        "origin_filename": doc.origin.filename,
        "mimetype": doc.origin.mimetype,
        #"num_pages": num_pages,
        "docling_version": doc.version,
        "num_text_blocks": len(doc.texts),
        "num_tables": len(doc.tables),
        "num_images": len(doc.pictures),
    }

    # =========================================================
    # 3️⃣ Extração de TEXTO (linearizado)
    # =========================================================
    text = doc.export_to_text()

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Texto extraído está vazio ou inválido.")

    # DEBUG CONTROLADO (opcional)
    #print(f"[OCR OK] '{pdf_name}' | {num_pages} páginas")
    #print(text[:1000])  # primeiras 1000 chars

    return {
        "text": text,
        "metadata": native_metadata
    }

result = process_pdf("Documento sobre RAG-ENG.pdf")

#print(result["metadata"])
#print(len(result["text"]))
