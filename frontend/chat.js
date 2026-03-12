document.addEventListener('DOMContentLoaded', () => {
    // Configure Marked for ChatGPT-style code blocks
    const renderer = new marked.Renderer();
    renderer.code = function (code, language) {
        const lang = language || 'plaintext';

        return `
<div class="code-block-wrapper">
    <div class="code-header">
        <span class="code-language">${lang}</span>
        <button class="copy-btn" onclick="copyCode(this)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
            <span>Copiar código</span>
        </button>
    </div>
    <div class="code-content">
        <pre><code class="language-${lang}">${code}</code></pre>
    </div>
</div>`;
    };

    marked.setOptions({
        renderer: renderer,
        breaks: true
    });

    const trigger = document.getElementById('roa-chat-trigger');
    const windowEl = document.getElementById('roa-chat-window');
    const closeBtn = document.getElementById('roa-close-chat');
    const sendBtn = document.getElementById('roa-send-btn');
    const userInput = document.getElementById('roa-user-input');
    const messagesContainer = document.getElementById('roa-chat-messages');
    const resizeHandle = document.getElementById('roa-resize-handle');

    const BASE_URL = 'http://localhost:8000/ROA';
    const API_URL = `${BASE_URL}/chat`;
    const LOGIN_URL = `${BASE_URL}/login`;
    let conversationId = null;
    let token = localStorage.getItem('roa_token');

    const isIframe = window.self !== window.top;

    const loginOverlay = document.getElementById('roa-login-overlay');
    const loginBtn = document.getElementById('roa-login-btn');
    const emailInput = document.getElementById('roa-email');
    const passwordInput = document.getElementById('roa-password');
    const loginError = document.getElementById('roa-login-error');

    function checkAuth() {
        if (!loginOverlay) return; // Skip if no overlay (e.g., on dashboard)
        if (token) {
            loginOverlay.classList.add('hidden');
            if (isIframe && userInput) {
                userInput.focus();
            }
        } else {
            loginOverlay.classList.remove('hidden');
        }
    }

    async function login() {
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        if (!email || !password) {
            loginError.textContent = 'Preencha todos os campos.';
            return;
        }

        loginBtn.disabled = true;
        loginBtn.textContent = 'Entrando...';
        loginError.textContent = '';

        try {
            // OAuth2PasswordRequestForm expects x-www-form-urlencoded
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const response = await fetch(LOGIN_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.access_token) {
                token = data.access_token;
                localStorage.setItem('roa_token', token);
                emailInput.value = '';
                passwordInput.value = '';
                checkAuth();
            } else {
                loginError.textContent = data.detail || 'Erro ao fazer login.';
            }
        } catch (error) {
            loginError.textContent = 'Erro de conexão com o servidor.';
            console.error('Login Error:', error);
        } finally {
            loginBtn.disabled = false;
            loginBtn.textContent = 'Acessar';
        }
    }

    if (loginBtn) {
        loginBtn.addEventListener('click', login);
    }
    if (passwordInput) {
        passwordInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') login();
        });
    }

    // --- Show/Hide Logic ---
    if (isIframe) {
        // In iframe mode, always show the window and hide the trigger
        windowEl.classList.remove('hidden');
        if (trigger) trigger.style.display = 'none';
        checkAuth();
    } else if (trigger) {
        trigger.addEventListener('click', () => {
            windowEl.classList.toggle('hidden');
            if (!windowEl.classList.contains('hidden')) {
                checkAuth();
            }
        });
    }

    closeBtn.addEventListener('click', () => {
        windowEl.classList.add('hidden');
    });

    // --- Message Logic ---
    function addMessage(content, role) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';

        if (role === 'system') {
            // Limpa as tags vindas do prompt da API
            let cleanContent = content
                .replace(/\[(?:EXPLANATION|EXPLICAÇÃO|Explicação)\]:?/gi, "**Explicação:**\n\n")
                .replace(/\[(?:CODE|CÓDIGO|Código|DATA\/CODE)\]:?/gi, "\n\n**Código:**\n\n")
                .replace(/\[(?:SOURCE|FONTE|Fonte)\]:?/gi, "\n\n**Fonte:**\n\n");

            // Render Markdown
            contentDiv.innerHTML = marked.parse(cleanContent);

            // Ativa o Highlight.js no DOM
            contentDiv.querySelectorAll('pre code').forEach((block) => {
                // Remove the extra "hljs" handling since highlightElement takes care of classes
                hljs.highlightElement(block);
            });
        } else {
            contentDiv.textContent = content;
        }

        msgDiv.appendChild(contentDiv);
        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        userInput.value = '';
        userInput.style.height = 'auto';

        // Add loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message system loading';
        loadingDiv.textContent = 'Pensando...';
        messagesContainer.appendChild(loadingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    question: text,
                    conversation_id: conversationId
                })
            });

            if (response.status === 401) {
                token = null;
                localStorage.removeItem('roa_token');
                checkAuth();
                messagesContainer.removeChild(loadingDiv);
                return;
            }

            const data = await response.json();
            messagesContainer.removeChild(loadingDiv);

            if (data.answer) {
                addMessage(data.answer, 'system');
                conversationId = data.conversation_id;
            } else {
                addMessage('Desculpe, ocorreu um erro na resposta.', 'system');
            }
        } catch (error) {
            messagesContainer.removeChild(loadingDiv);
            addMessage('Erro de conexão com o servidor.', 'system');
            console.error('API Error:', error);
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
    });

    // --- Resize Logic ---
    let isResizing = false;
    let initialWidth, initialHeight, initialMouseX, initialMouseY, aspectRatio;

    resizeHandle.addEventListener('mousedown', (e) => {
        isResizing = true;
        initialWidth = windowEl.offsetWidth;
        initialHeight = windowEl.offsetHeight;
        initialMouseX = e.clientX;
        initialMouseY = e.clientY;
        aspectRatio = initialWidth / initialHeight;

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', stopResizing);
        e.preventDefault();
    });

    function handleMouseMove(e) {
        if (!isResizing) return;

        // Calculate delta (negative because we are pulling from top-left)
        const dx = initialMouseX - e.clientX;
        const dy = initialMouseY - e.clientY;

        // Option: Proportional resize
        // Let's use the larger delta to drive the resize
        let newWidth, newHeight;

        if (Math.abs(dx) > Math.abs(dy)) {
            newWidth = initialWidth + dx;
            newHeight = newWidth / aspectRatio;
        } else {
            newHeight = initialHeight + dy;
            newWidth = newHeight * aspectRatio;
        }

        // Min and Max constraints
        if (newWidth > 300 && newWidth < 800) {
            windowEl.style.width = newWidth + 'px';
            windowEl.style.height = newHeight + 'px';
        }
    }

    function stopResizing() {
        isResizing = false;
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', stopResizing);
    }
});

// Global copy function for the "Copy Code" button
window.copyCode = function (button) {
    const wrapper = button.closest('.code-block-wrapper');
    const code = wrapper.querySelector('code').innerText;

    navigator.clipboard.writeText(code).then(() => {
        const span = button.querySelector('span');
        const originalText = span.innerText;
        const icon = button.querySelector('svg');
        const originalIcon = icon.innerHTML;

        // Show checkmark
        icon.innerHTML = '<polyline points="20 6 9 17 4 12"></polyline>';
        span.innerText = 'Copiado!';

        setTimeout(() => {
            span.innerText = originalText;
            icon.innerHTML = originalIcon;
        }, 2000);
    });
};

