# ROA Chat Widget

Este front-end permite integrar o assistente ROA em qualquer site.

## Como Implementar

### 1. Via Script (Recomendado)
Adicione o seguinte código antes do fechamento da tag `</body>` do seu site:

```html
<link rel="stylesheet" href="https://elna-semitheatric-cinthia.ngrok-free.dev/static/frontend/style.css">
<div id="roa-chat-container"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/11.1.1/marked.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://elna-semitheatric-cinthia.ngrok-free.dev/static/frontend/chat.js"></script>
```

### 2. Via Iframe
Você pode criar uma página hospedada com este widget e chamá-la:

```html
<iframe src="https://sua-url-frontend.com" style="border:none; width:100%; height:100%;"></iframe>
```

## Funcionalidades
- **Redimensionável**: Clique no canto superior esquerdo da janela do chat para arrastar e mudar o tamanho mantendo a proporção.
- **Destaque de Código**: Suporta blocos de código (Python, TS, Bash, etc.) com cores e formatação estilo ChatGPT.
- **Design Premium**: Glassmorphism e animações suaves.
- **Conexão Direta**: Configurado para falar com o endpoint de RAG.

## Customização Adicional
Para mudar a cor principal, altere a variável `--primary-gradient` no arquivo `style.css`.
