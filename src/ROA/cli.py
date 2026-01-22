from ROA.services import init_knowledge_base, answer_question


def main():
    # PDF base de conhecimento
    pdf_name = "Documento sobre RAG-ENG.pdf"

    # Inicializa base de conhecimento (indexação ocorre uma única vez)
    vector_store = init_knowledge_base(pdf_name)

    print(f"Documento carregado: {pdf_name}")
    print("Digite sua pergunta ou 'sair' para encerrar.")

    # Loop interativo (CLI)
    while True:
        question = input("\nPergunta: ").strip()

        if not question:
            continue

        if question.lower() in ("sair", "exit", "quit"):
            print("Encerrando...")
            break

        answer = answer_question(
            question=question,
            vector_store=vector_store
        )

        if not answer:
            print("Não foi possível gerar resposta.")
            continue

        print("\n===== ANSWER =====\n")
        print(answer)


if __name__ == "__main__":
    main()
