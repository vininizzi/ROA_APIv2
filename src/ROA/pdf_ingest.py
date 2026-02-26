from langchain_community.document_loaders import PyMuPDFLoader
import pprint

file_path = "/home/brain/projects/RAG para PDFs/RAG com OCR do Vini/ROA - RAG com OCR Academico/Documentos/2.pdf"
loader = PyMuPDFLoader(file_path)
docs = loader.load()

pages = []
for doc in loader.lazy_load():
    pages.append(doc)
    if len(pages) >= 10:
        # do some paged operation, e.g.
        # index.upsert(page)

        pages = []
print(len(pages))


print(pages[0].page_content[:100])
pprint.pp(pages[1].metadata)