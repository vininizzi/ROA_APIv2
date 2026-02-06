import os
import time
import requests
from tqdm import tqdm

BASE_URL = "https://pergamum.facens.br/pergamum/biblioteca"

TEMAS = {
    "computacao": "computação",
    "arquitetura": "arquitetura"
}

LIVROS_POR_TEMA = 10
DELAY = 1

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
})


def buscar_acervos(termo):
    """
    Retorna lista de IDs de acervo para o termo buscado
    """
    url = f"{BASE_URL}/acervos-indexados"
    params = {"q": termo}

    r = session.get(url, params=params)
    r.raise_for_status()

    data = r.json()
    return data.get("acervos", [])


def buscar_links(acervos):
    """
    Retorna links associados aos acervos (PDFs)
    """
    url = f"{BASE_URL}/links-resultado"
    params = {"acervos": ",".join(map(str, acervos))}

    r = session.get(url, params=params)
    r.raise_for_status()

    return r.json()


def baixar_pdf(url_pdf, destino):
    r = session.get(url_pdf)
    r.raise_for_status()

    with open(destino, "wb") as f:
        f.write(r.content)


def processar_tema(pasta, termo):
    print(f"\n🔍 Tema: {termo}")
    os.makedirs(pasta, exist_ok=True)

    acervos = buscar_acervos(termo)
    acervos = acervos[:LIVROS_POR_TEMA]

    if not acervos:
        print("⚠️ Nenhum acervo encontrado.")
        return

    links_info = buscar_links(acervos)

    contador = 0
    for item in tqdm(links_info):
        if contador >= LIVROS_POR_TEMA:
            break

        url_pdf = item.get("url")
        if not url_pdf or not url_pdf.lower().endswith(".pdf"):
            continue

        nome_arquivo = f"livro_{contador+1}.pdf"
        caminho = os.path.join(pasta, nome_arquivo)

        try:
            baixar_pdf(url_pdf, caminho)
            contador += 1
        except Exception as e:
            print(f"❌ Erro ao baixar: {e}")

        time.sleep(DELAY)


def main():
    for pasta, termo in TEMAS.items():
        processar_tema(pasta, termo)


if __name__ == "__main__":
    main()
