import requests

def test_chat():
    url = "http://localhost:8000/ROA/chat"
    payload = {
        "question": "Can you show me a simple Hello World program in JavaScript?"
    }
    
    print("Enviando requisição...")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        print("\n--- Resposta da API ---")
        print(data.get('answer', 'No answer found'))
        print("-----------------------")
        
        if "```javascript" in data.get('answer', '').lower() or "```js" in data.get('answer', '').lower():
            print("\n✅ Sucesso: O assistant retornou o bloco de código Markdown com o identificador da linguagem.")
        else:
            print("\n⚠️ Aviso: Verifique a resposta acima para confirmar se a formatação Markdown está presente.")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_chat()
