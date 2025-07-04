document.addEventListener('DOMContentLoaded', () => {
    console.log('Chat globale inizializzata');
    
    // 1. ELEMENTI DOM
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const emojiButton = document.getElementById('emoji-btn');
    const chatActions = document.querySelector('.chat-actions');
    const typingIndicator = document.getElementById('typing-indicator');

    // 2. VARIABILI GLOBALI
    let isTyping = false;
    let typingTimeout;
    const TYPING_DELAY = 2000; // 2 secondi

    // 3. INIZIALIZZAZIONE EMOJI PICKER
    function initEmojiPicker() {
        try {
            // Verifica se il componente è disponibile
            if (typeof customElements.get('emoji-picker') === 'undefined') {
                console.warn('emoji-picker-element non disponibile, attivo fallback');
                setupEmojiFallback();
                return;
            }

            // Crea container per il picker
            const pickerContainer = document.createElement('div');
            pickerContainer.className = 'emoji-picker-container';
            
            // Crea l'emoji picker
            const picker = document.createElement('emoji-picker');
            picker.setAttribute('locale', 'it');
            
            // Stile del picker
            Object.assign(picker.style, {
                position: 'absolute',
                bottom: '60px',
                right: '0',
                zIndex: '1000',
                display: 'none',
                width: '350px',
                maxHeight: '400px',
                borderRadius: '12px',
                boxShadow: '0 5px 15px rgba(0,0,0,0.3)',
                border: '1px solid #4a5568'
            });

            pickerContainer.appendChild(picker);
            chatActions.appendChild(pickerContainer);

            // Gestione eventi
            emojiButton.addEventListener('click', toggleEmojiPicker);
            picker.addEventListener('emoji-click', insertEmoji);
            document.addEventListener('click', closeEmojiPicker);

            function toggleEmojiPicker(e) {
                e.stopPropagation();
                picker.style.display = picker.style.display === 'none' ? 'block' : 'none';
            }

            function insertEmoji(event) {
                messageInput.value += event.detail.unicode;
                messageInput.focus();
                picker.style.display = 'none';
                updateTypingStatus();
            }

            function closeEmojiPicker(e) {
                if (!pickerContainer.contains(e.target)){
                    picker.style.display = 'none';
                }
            }

            console.log('Emoji picker inizializzato con successo');
        } catch (error) {
            console.error('Errore inizializzazione emoji picker:', error);
            setupEmojiFallback();
        }
    }

    // 4. FALLBACK EMOJI
    function setupEmojiFallback() {
        try {
            const emojis = ['😀','😂','😍','😊','👍','❤️','🎉','🙏','🔥','😎','🤔','😢'];
            const fallbackContainer = document.createElement('div');
            fallbackContainer.className = 'emoji-fallback';
            
            Object.assign(fallbackContainer.style, {
                position: 'absolute',
                bottom: '60px',
                right: '0',
                background: '#2d3748',
                borderRadius: '8px',
                padding: '8px',
                display: 'grid',
                gridTemplateColumns: 'repeat(6, 1fr)',
                gap: '4px',
                zIndex: '1000',
                display: 'none',
                width: '300px',
                maxHeight: '300px',
                overflowY: 'auto',
                boxShadow: '0 5px 15px rgba(0,0,0,0.3)',
                border: '1px solid #4a5568'
            });

            emojis.forEach(emoji => {
                const btn = document.createElement('button');
                btn.textContent = emoji;
                
                Object.assign(btn.style, {
                    background: 'none',
                    border: 'none',
                    fontSize: '1.5rem',
                    cursor: 'pointer',
                    padding: '4px',
                    transition: 'transform 0.2s',
                    borderRadius: '4px'
                });
                
                btn.addEventListener('click', () => {
                    messageInput.value += emoji;
                    messageInput.focus();
                    fallbackContainer.style.display = 'none';
                    updateTypingStatus();
                });
                
                btn.addEventListener('mouseover', () => btn.style.transform = 'scale(1.2)');
                btn.addEventListener('mouseout', () => btn.style.transform = 'scale(1)');
                
                fallbackContainer.appendChild(btn);
            });

            chatActions.appendChild(fallbackContainer);

            emojiButton.addEventListener('click', (e) => {
                e.stopPropagation();
                fallbackContainer.style.display = 
                    fallbackContainer.style.display === 'none' ? 'grid' : 'none';
            });

            document.addEventListener('click', (e) => {
                if (!fallbackContainer.contains(e.target) && e.target !== emojiButton) {
                    fallbackContainer.style.display = 'none';
                }
            });

            console.log('Fallback emoji inizializzato');
        } catch (error) {
            console.error('Errore inizializzazione fallback emoji:', error);
        }
    }

    // 5. GESTIONE MESSAGGI
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        try {
            const response = await fetch('/chat/api/global/send/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN,
                },
                body: JSON.stringify({ content: message })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            if (data.status === 'success') {
                messageInput.value = '';
                addMessageToChat(data.message, true);
                resetTypingStatus();
            }
        } catch (error) {
            console.error('Errore invio messaggio:', error);
            alert(`Errore durante l'invio: ${error.message}`);
        }
    }

    function addMessageToChat(messageData, isOwn = false) {
        try {
            const messageElement = document.createElement('article');
            messageElement.className = `chat-message ${isOwn ? 'own' : 'other'}`;
            messageElement.dataset.msgId = messageData.id;

            const profilePic = messageData.sender.profile_picture || DEFAULT_PROFILE_PIC;
            const profilePicHtml = `<img src="${profilePic}" 
                                       alt="${messageData.sender.username}" 
                                       class="chat-user-pic"
                                       onerror="this.src='${DEFAULT_PROFILE_PIC}'">`;

            messageElement.innerHTML = `
                <div class="chat-meta">
                    <strong class="chat-user" title="${messageData.sender.email || 'No email'}">
                        ${profilePicHtml}
                        ${messageData.sender.username}
                    </strong>
                    <time datetime="${messageData.timestamp}">${messageData.timestamp}</time>
                </div>
                <div class="chat-text">${messageData.content}</div>
                ${!isOwn ? `<button class="report-btn" data-msg-id="${messageData.id}">⚠️ Segnala</button>` : ''}
            `;

            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } catch (error) {
            console.error('Errore aggiunta messaggio:', error);
        }
    }

    // 6. TYPING INDICATOR
    function updateTypingStatus() {
        if (!isTyping) {
            isTyping = true;
            // Invia notifica "sta scrivendo" al server
            // Implementa questa parte secondo le tue esigenze
        }
        
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(resetTypingStatus, TYPING_DELAY);
    }

    function resetTypingStatus() {
        isTyping = false;
        // Invia notifica "ha smesso di scrivere" al server
    }

    // 7. CARICAMENTO MESSAGGI
    async function loadMessages() {
        try {
            const response = await fetch('/chat/api/global/messages/');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const messages = await response.json();
            chatMessages.innerHTML = '';
            messages.forEach(msg => addMessageToChat(msg, msg.is_own));
        } catch (error) {
            console.error('Errore caricamento messaggi:', error);
        }
    }

    // 8. GESTIONE REPORT
    function handleReportClick(e) {
        if (e.target.classList.contains('report-btn')) {
            const messageId = e.target.dataset.msgId;
            // Implementa la logica di report qui
            alert(`Messaggio ${messageId} segnalato`);
        }
    }

    // 9. INIZIALIZZAZIONE
    function init() {
        if (!emojiButton || !messageInput || !sendButton || !chatMessages) {
            console.error('Elementi DOM mancanti');
            return;
        }

        initEmojiPicker();
        
        // Event listeners
        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        messageInput.addEventListener('input', updateTypingStatus);
        chatMessages.addEventListener('click', handleReportClick);
        
        // Carica messaggi iniziali e imposta refresh
        loadMessages();
        setInterval(loadMessages, 50000) // Aggiorna ogni 5 secondi
    }

    // AVVIA L'APPLICAZIONE
    init();
});

const chatForm = document.getElementById('chat-form');
if (chatForm) {
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault(); // ⚠️ Impedisce il reload
        sendMessage();
    });
}
