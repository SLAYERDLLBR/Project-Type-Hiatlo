document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const suggestionButtons = document.querySelectorAll('.suggestion-btn');

    function addMessage(text, sender) { // sender pode ser 'user' ou 'valerium'
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('message-wrapper', `${sender}-message`);

        const messageBox = document.createElement('div');
        messageBox.classList.add('message-box');

        const senderNameSpan = document.createElement('span');
        senderNameSpan.classList.add('sender-name');
        senderNameSpan.textContent = sender === 'user' ? 'Você' : 'Valerium';

        const messageTextP = document.createElement('p');
        messageTextP.classList.add('message-text');
        messageTextP.textContent = text; // Para texto simples. Se a IA retornar HTML, use innerHTML com cuidado.

        messageBox.appendChild(senderNameSpan);
        messageBox.appendChild(messageTextP);
        messageWrapper.appendChild(messageBox);
        chatMessages.appendChild(messageWrapper);

        // Scroll para a última mensagem
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessageToBackend(message) {
        addMessage(message, 'user');
        userInput.value = '';
        loadingIndicator.style.display = 'block';
        chatMessages.scrollTop = chatMessages.scrollHeight;


        try {
            // Esta é a URL para onde o frontend enviará a mensagem.
            // Quando você rodar o Flask, ele estará em algo como http://127.0.0.1:5000/chat
            const response = await fetch('/chat', { // O endpoint que criaremos no Flask
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });

            loadingIndicator.style.display = 'none';

            if (!response.ok) {
                const errorData = await response.json();
                addMessage(errorData.error || 'Erro ao conectar com Valerium.', 'valerium');
                return;
            }

            const data = await response.json();
            addMessage(data.reply, 'valerium');

        } catch (error) {
            loadingIndicator.style.display = 'none';
            console.error('Erro ao enviar mensagem:', error);
            addMessage('Não foi possível conectar ao servidor de Valerium. Tente novamente mais tarde.', 'valerium');
        }
    }

    sendButton.addEventListener('click', () => {
        const message = userInput.value.trim();
        if (message) {
            sendMessageToBackend(message);
        }
    });

    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            const message = userInput.value.trim();
            if (message) {
                sendMessageToBackend(message);
            }
        }
    });

    suggestionButtons.forEach(button => {
        button.addEventListener('click', () => {
            const suggestionText = button.textContent;
            userInput.value = suggestionText; // Opcional: preencher o campo de entrada
            sendMessageToBackend(suggestionText);
        });
    });

    // Adicionar mensagem de boas-vindas inicial se não estiver no HTML estático
    // addMessage("Saudações! Sou Valerium. O que você deseja desvendar sobre a história?", "valerium");
});