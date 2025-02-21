document.addEventListener('DOMContentLoaded', function() {
    const messagesContainer = document.getElementById('messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');

    // Simple Enter key handler
    messageInput.addEventListener('keydown', function(e) {
        // If Enter without Shift, send message
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const message = messageInput.value.trim();
            if (message !== '') {
                sendMessage();
            }
        }
    });

    // Send button click handler
    sendButton.addEventListener('click', function() {
        const message = messageInput.value.trim();
        if (message !== '') {
            sendMessage();
        }
    });

    // Function to send messages
    async function sendMessage() {
        const message = messageInput.value.trim();
        
        // Clear input and reset height
        messageInput.value = '';
        messageInput.style.height = 'auto';
        
        // Add user message to UI
        addMessageToUI('user', message);
        
        // Show loading indicator
        const loadingRow = createLoadingIndicator();
        messagesContainer.appendChild(loadingRow);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        try {
            // Make API call
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });
            
            const data = await response.json();
            
            // Remove loading indicator
            const loadingIndicator = document.getElementById('loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.remove();
            }

            if (data.error) {
                console.error('Error:', data.error);
                addMessageToUI('bot', data.error, true);
            } else {
                addMessageToUI('bot', data.response);
            }
            
            
        } catch (error) {
            console.error('Error:', error);
            // Remove loading indicator
            const loadingIndicator = document.getElementById('loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.remove();
            }
            // Add error message
            addMessageToUI('bot', 'Sorry, there was an error processing your request.');
        }
    }

    // Create loading indicator
    function createLoadingIndicator() {
        const loadingRow = document.createElement('div');
        loadingRow.classList.add('message-row');
        loadingRow.id = 'loading-indicator';
        
        const botAvatar = document.createElement('div');
        botAvatar.classList.add('bot-avatar');
        botAvatar.innerHTML = `<img src="https://arkalos.com/assets/img/arkalos-logo.png" alt="Arkalos Logo" class="avatar-logo">`;
        
        const loadingMessage = document.createElement('div');
        loadingMessage.classList.add('message', 'bot', 'typing-indicator');
        
        const loader = document.createElement('div');
        loader.classList.add('loader');
        
        const text = document.createElement('p');
        text.innerText = 'Thinking...';
        
        loadingMessage.appendChild(loader);
        loadingMessage.appendChild(text);
        
        loadingRow.appendChild(botAvatar);
        loadingRow.appendChild(loadingMessage);
        
        return loadingRow;
    }

    // Process markdown text and convert to HTML
    function processMarkdown(text) {
        if (!text) return '';
        
        // Create a showdown converter with tables extension enabled
        const converter = new showdown.Converter({
            tables: true,
            tableHeaderId: false,
            strikethrough: true,
            tasklists: true
        });
        
        // Convert markdown to HTML
        const html = converter.makeHtml(text);
        
        // Add our custom class to tables
        return html.replace(/<table>/g, '<table class="markdown-table">');
    }

    /**
     * Escape HTML special characters to prevent XSS attacks
     */
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Add message to UI with markdown support
    function addMessageToUI(sender, text, is_error = false) {
        const messageRow = document.createElement('div');
        messageRow.classList.add('message-row');
        
        if (sender === 'bot') {
            const botAvatar = document.createElement('div');
            botAvatar.classList.add('bot-avatar');
            botAvatar.innerHTML = `<img src="https://arkalos.com/assets/img/arkalos-logo.png" alt="Arkalos Logo" class="avatar-logo">`;
            messageRow.appendChild(botAvatar);
            
            const messageElement = document.createElement('div');
            messageElement.classList.add('message', sender);
            // Process markdown for bot messages
            if (is_error) {
                messageElement.classList.add('error');
                messageElement.innerHTML = '<p> ⚠️' + escapeHtml(text) + '</p>'
            } else {
                messageElement.innerHTML = processMarkdown(text);
            }
            
            messageRow.appendChild(messageElement);
        } else {
            const placeholder = document.createElement('div');
            placeholder.classList.add('avatar-placeholder');
            messageRow.appendChild(placeholder);
            
            const messageElement = document.createElement('div');
            messageElement.classList.add('message', sender);
            // No markdown processing for user messages
            messageElement.textContent = text;
            
            messageRow.appendChild(messageElement);
        }
        
        messagesContainer.appendChild(messageRow);
        
        // Add syntax highlighting if prism.js is available
        if (window.Prism) {
            Prism.highlightAllUnder(messageRow);
        }
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
});