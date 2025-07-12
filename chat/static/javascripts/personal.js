document.addEventListener('DOMContentLoaded', () => {
    // --- Gestione tema chiaro/scuro ---
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-theme');
    }

    const toggleButton = document.createElement('button');
    toggleButton.textContent = 'Cambia Tema';
    toggleButton.className = 'theme-toggle';
    document.body.appendChild(toggleButton);

    toggleButton.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
    });

    // --- Variabili DOM per chat ---
    const messagesContainer = document.getElementById('messages');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-content');
    const sendButton = messageForm.querySelector('.send-button');
    const editMessageModal = document.getElementById('edit-message-modal');
    const editMessageForm = document.getElementById('edit-message-form');
    const editMessageContent = document.getElementById('edit-message-content');
    const editMessageIdInput = document.getElementById('edit-message-id');

    // Stato
    let currentEditMessageId = null;
    let isWebSocketConnected = false;
    let socket = null;
    let messageQueue = [];

    // Inizializzazione chat
    initChat();

    function initChat() {
        setupEventListeners();
        setupMessageInput();
        connectWebSocket();
        scrollToBottom();
        setupTooltips();
        loadMessages(); // Carica messaggi iniziali
    }

    function setupEventListeners() {
        messageForm.addEventListener('submit', handleMessageSubmit);
        editMessageForm.addEventListener('submit', handleEditSubmit);
        editMessageModal.querySelector('.close-modal').addEventListener('click', closeEditModal);
        editMessageModal.querySelector('.btn-cancel').addEventListener('click', closeEditModal);
        messagesContainer.addEventListener('click', handleMessageActions);

        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                loadMessages();
            }
        });
    }

    function setupMessageInput() {
        messageInput.addEventListener('input', () => {
            sendButton.disabled = !messageInput.value.trim();

            messageInput.style.height = 'auto';
            messageInput.style.height = `${Math.min(messageInput.scrollHeight, 150)}px`;
        });

        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (messageInput.value.trim()) {
                    handleMessageSubmit(e);
                }
            }
        });
    }

    async function handleMessageSubmit(e) {
        e.preventDefault();
        const content = messageInput.value.trim();
        if (!content) return;

        sendButton.disabled = true;
        messageInput.disabled = true;

        try {
            if (isWebSocketConnected) {
                socket.send(JSON.stringify({
                    type: 'new_message',
                    content: content,
                    conversation_id: getConversationIdFromUrl()
                }));
            } else {
                const response = await fetch(messageForm.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({ content: content })
                });

                if (!response.ok) throw new Error('Errore durante l\'invio');

                const data = await response.json();
                appendMessage(data);
            }

            messageInput.value = '';
            messageInput.style.height = 'auto';
            sendButton.disabled = true;
        } catch (error) {
            console.error('Errore invio messaggio:', error);
            showToast('Errore durante l\'invio del messaggio', 'error');
        } finally {
            messageInput.disabled = false;
            messageInput.focus();
        }
    }

    function connectWebSocket() {
        const wsScheme = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsUrl = wsScheme + window.location.host + '/ws/chat/' + getConversationIdFromUrl() + '/';

        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            isWebSocketConnected = true;
            console.log('WebSocket connesso');

            if (messageQueue.length > 0) {
                messageQueue.forEach(msg => socket.send(JSON.stringify(msg)));
                messageQueue = [];
            }
        };

        socket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            handleWebSocketMessage(data);
        };

        socket.onclose = () => {
            isWebSocketConnected = false;
            console.log('WebSocket disconnesso');
            setTimeout(connectWebSocket, 5000);
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    function handleWebSocketMessage(data) {
        switch (data.type) {
            case 'new_message':
                appendMessage(data.message);
                break;
            case 'message_updated':
                updateMessage(data.message);
                break;
            case 'message_deleted':
                removeMessage(data.message_id);
                break;
            case 'user_status':
                updateUserStatus(data.user_id, data.status);
                break;
            case 'typing_indicator':
                showTypingIndicator(data.user_id, data.is_typing);
                break;
        }
    }

    async function loadMessages() {
        try {
            const response = await fetch(`${window.location.pathname}?format=json`);
            if (!response.ok) throw new Error('Errore nel caricamento');

            const data = await response.json();
            renderMessages(data.messages);
            updateConversationStatus(data.conversation_status);
        } catch (error) {
            console.error('Errore caricamento messaggi:', error);
        }
    }

    function renderMessages(messages) {
        messagesContainer.innerHTML = '';

        if (messages.length === 0) {
            messagesContainer.innerHTML = `
                <div class="no-messages">
                    <i class="fas fa-comments"></i>
                    <p>Nessun messaggio in questa conversazione. Inizia a chattare!</p>
                </div>
            `;
            return;
        }

        messages.forEach(message => appendMessage(message, false));
        scrollToBottom();
    }

    function appendMessage(message, scroll = true) {
        const noMessages = messagesContainer.querySelector('.no-messages');
        if (noMessages) noMessages.remove();

        const messageElement = createMessageElement(message);
        messagesContainer.appendChild(messageElement);

        if (scroll) scrollToBottom();

        if (message.sender === currentUserId() && !message.is_read) {
            setTimeout(() => markMessageAsRead(message.message_id), 1000);
        }
    }

    function createMessageElement(message) {
        const isOwn = message.sender === currentUserId();
        const messageElement = document.createElement('div');

        messageElement.className = `message ${isOwn ? 'sent' : 'received'}`;
        messageElement.dataset.messageId = message.message_id;
        messageElement.dataset.senderId = message.sender;
        messageElement.innerHTML = `
            <div class="message-content">
                <div class="message-header">
                    <strong>${escapeHtml(message.sender_username)}</strong>
                    <div class="message-status">
                        ${message.is_edited ? `
                            <span class="edited-indicator" title="Modificato">
                                <i class="fas fa-pencil-alt"></i>
                            </span>` : ''}
                        ${message.is_read && isOwn ? `
                            <span class="read-indicator" title="Letto">
                                <i class="fas fa-check-double"></i>
                            </span>` : ''}
                    </div>
                </div>
                <p class="message-text">${escapeHtml(message.content)}</p>
                <div class="message-footer">
                    <small class="message-timestamp" title="${formatFullTimestamp(message.timestamp)}">
                        ${formatTime(message.timestamp)}
                    </small>
                    ${isOwn ? `
                        <div class="message-actions">
                            <button class="btn-message-action edit-btn" data-tooltip="Modifica">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn-message-action delete-btn" data-tooltip="Elimina">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>` : ''}
                </div>
                <span class="message-id">Msg ID: ${message.message_id}</span>
            </div>
        `;
        return messageElement;
    }

    function handleMessageActions(e) {
        const messageElement = e.target.closest('.message');
        if (!messageElement) return;

        const messageId = messageElement.dataset.messageId;

        if (e.target.closest('.edit-btn')) {
            const messageContent = messageElement.querySelector('.message-text').textContent;
            openEditModal(messageId, messageContent);
        }

        if (e.target.closest('.delete-btn')) {
            if (confirm('Sei sicuro di voler eliminare questo messaggio?')) {
                deleteMessage(messageId);
            }
        }
    }

    function openEditModal(messageId, content) {
        currentEditMessageId = messageId;
        editMessageContent.value = content;
        editMessageIdInput.value = messageId;
        editMessageModal.style.display = 'flex';
        editMessageContent.focus();
    }

    function closeEditModal() {
        editMessageModal.style.display = 'none';
        currentEditMessageId = null;
    }

    async function handleEditSubmit(e) {
        e.preventDefault();
        const newContent = editMessageContent.value.trim();

        if (!newContent || !currentEditMessageId) return;

        try {
            const response = await fetch(`/api/messages/${currentEditMessageId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ content: newContent })
            });

            if (!response.ok) throw new Error('Errore durante la modifica');

            const data = await response.json();
            updateMessage(data);
            closeEditModal();
        } catch (error) {
            console.error('Errore modifica messaggio:', error);
            showToast('Errore durante la modifica del messaggio', 'error');
        }
    }

    async function deleteMessage(messageId) {
        try {
            const response = await fetch(`/api/messages/${messageId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            });

            if (!response.ok) throw new Error('Errore durante l\'eliminazione');

            removeMessage(messageId);
        } catch (error) {
            console.error('Errore eliminazione messaggio:', error);
            showToast('Errore durante l\'eliminazione del messaggio', 'error');
        }
    }

    function removeMessage(messageId) {
        const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
        if (messageElement) messageElement.remove();

        if (messagesContainer.children.length === 0) {
            messagesContainer.innerHTML = `
                <div class="no-messages">
                    <i class="fas fa-comments"></i>
                    <p>Nessun messaggio in questa conversazione. Inizia a chattare!</p>
                </div>
            `;
        }
    }

    async function markMessageAsRead(messageId) {
        try {
            await fetch(`/api/messages/${messageId}/mark_as_read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            });

            const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
            if (messageElement) {
                const readIndicator = messageElement.querySelector('.read-indicator');
                if (!readIndicator) {
                    messageElement.querySelector('.message-status').insertAdjacentHTML('beforeend', `
                        <span class="read-indicator" title="Letto">
                            <i class="fas fa-check-double"></i>
                        </span>
                    `);
                }
            }
        } catch (error) {
            console.error('Errore segnatura messaggio come letto:', error);
        }
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function getConversationIdFromUrl() {
        // Presume URL tipo /chat/conversation/<uuid>/
        const parts = window.location.pathname.split('/').filter(Boolean);
        return parts[parts.length - 1];
    }

    function currentUserId() {
        // Assumi di avere dataset userId nel body (es. <body data-user-id="{{ request.user.id }}">)
        return parseInt(document.body.dataset.userId);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatTime(timestamp) {
        return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function formatFullTimestamp(timestamp) {
        return new Date(timestamp).toLocaleString();
    }

    function showToast(message, type = 'success') {
        // Semplice console.log, da implementare con UI toast se vuoi
        console.log(`${type}: ${message}`);
    }

    function setupTooltips() {
        // Puoi inizializzare tooltip se usi qualche libreria, o lasciare vuoto
    }
});
