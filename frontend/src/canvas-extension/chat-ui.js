// Chat UI Component
// Creates and manages the chat interface
// Note: API_BASE is defined in content.js

const CHAT_SERVER_URL = 'http://localhost:5000';

// Get session token from localStorage
function getSessionToken() {
    return localStorage.getItem('ubc_session_token') || 'qRrl-skZBpTUo3QSsb0QOexTda6HWVozH3AgfFQ7rfU';
}

let chatClient = null;
let currentChatRoom = null;
let typingTimeout = null;

// Initialize chat client
async function initializeChatClient() {
    if (!chatClient) {
        chatClient = new ChatClient(CHAT_SERVER_URL, getSessionToken());

        try {
            await chatClient.connect();
            console.log('Chat client connected');

            // Setup event handlers
            chatClient.onMessage((message, isEdit) => {
                if (currentChatRoom && message.room_id == currentChatRoom.id) {
                    if (isEdit) {
                        updateMessageInUI(message);
                    } else {
                        addMessageToUI(message);
                    }
                }
            });

            chatClient.onTyping((data) => {
                if (currentChatRoom && data.room_id == currentChatRoom.id) {
                    showTypingIndicator(data.user_id, data.is_typing);
                }
            });

            chatClient.onUserJoin((data) => {
                if (currentChatRoom && data.room_id == currentChatRoom.id) {
                    showSystemMessage(`User ${data.user_id} joined`);
                }
            });

            chatClient.onUserLeave((data) => {
                if (currentChatRoom && data.room_id == currentChatRoom.id) {
                    showSystemMessage(`User ${data.user_id} left`);
                }
            });

        } catch (error) {
            console.error('Failed to connect chat client:', error);
            throw error;
        }
    }
    return chatClient;
}

// Open chat for a specific room
async function openChat(roomId, roomName, roomType) {
    try {
        // Initialize client if needed
        await initializeChatClient();

        // Leave previous room if any
        if (currentChatRoom) {
            chatClient.leaveRoom(currentChatRoom.id);
        }

        // Set current room
        currentChatRoom = { id: roomId, name: roomName, type: roomType };

        // Join the room
        chatClient.joinRoom(roomId);

        // Show chat UI
        showChatModal(roomId, roomName, roomType);

        // Load message history
        await loadMessageHistory(roomId);

    } catch (error) {
        console.error('Error opening chat:', error);
        alert('Failed to open chat. Please try again.');
    }
}

// Show chat modal
function showChatModal(roomId, roomName, roomType) {
    // Remove existing modal if present
    let existingModal = document.getElementById('chat-modal');
    if (existingModal) {
        existingModal.remove();
    }

    const modal = document.createElement('div');
    modal.id = 'chat-modal';
    modal.innerHTML = `
        <div class="chat-modal-overlay">
            <div class="chat-modal-container">
                <div class="chat-header">
                    <div>
                        <h3>${roomName}</h3>
                        <span class="chat-room-type">${roomType.toUpperCase()}</span>
                    </div>
                    <button class="chat-close-btn" id="chat-close-btn">&times;</button>
                </div>

                <div class="chat-messages" id="chat-messages">
                    <div class="loading-messages">Loading messages...</div>
                </div>

                <div class="chat-typing-indicator" id="typing-indicator" style="display:none;">
                    <span></span>
                </div>

                <div class="chat-input-container">
                    <input
                        type="text"
                        id="chat-input"
                        placeholder="Type a message..."
                    />
                    <button id="chat-send-btn" class="chat-send-btn">Send</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Setup event listeners for chat controls
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');
    const closeBtn = document.getElementById('chat-close-btn');

    if (chatInput) {
        chatInput.addEventListener('keypress', handleChatKeyPress);
        chatInput.addEventListener('input', handleTyping);
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', sendChatMessage);
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', closeChat);
    }

    // Focus input
    setTimeout(() => {
        if (chatInput) chatInput.focus();
    }, 100);
}

// Load message history
async function loadMessageHistory(roomId) {
    try {
        // Use safeFetch from content.js with Bearer token
        const messages = await window.safeFetch(`${window.API_BASE}/rooms/${roomId}/messages`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${getSessionToken()}`,
                'Content-Type': 'application/json'
            }
        });
        console.log('Message history loaded:', messages);

        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.innerHTML = '';

        if (messages.length === 0) {
            messagesContainer.innerHTML = '<div class="no-messages">No messages yet. Start the conversation!</div>';
        } else {
            messages.forEach(message => addMessageToUI(message));
            scrollToBottom();

            // Set the last message ID for this room to avoid re-adding these messages during polling
            if (chatClient && messages.length > 0) {
                const latestMessage = messages[messages.length - 1];
                chatClient.lastMessageIdByRoom[roomId] = latestMessage.id;
            }
        }

    } catch (error) {
        console.error('Error loading messages:', error);
        document.getElementById('chat-messages').innerHTML = '<div class="error-messages">Failed to load messages</div>';
    }
}

// Add message to UI
function addMessageToUI(message) {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) return;

    // Remove "no messages" placeholder
    const noMessages = messagesContainer.querySelector('.no-messages');
    if (noMessages) noMessages.remove();

    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message';
    messageDiv.dataset.messageId = message.id;

    // Format timestamp in PST with date
    const messageDate = new Date(message.created_at);
    const now = new Date();
    const isToday = messageDate.toDateString() === now.toDateString();

    let timestamp;
    if (isToday) {
        // Today: just show time
        timestamp = messageDate.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            timeZone: 'America/Los_Angeles'
        });
    } else {
        // Other days: show date + time
        timestamp = messageDate.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            timeZone: 'America/Los_Angeles'
        });
    }

    const userName = message.user_name || `User ${message.user_id}`;

    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-user">${escapeHtml(userName)}</span>
            <span class="message-time">${timestamp}</span>
        </div>
        <div class="message-content">${escapeHtml(message.content)}</div>
    `;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Update message in UI (for edits)
function updateMessageInUI(message) {
    const messageDiv = document.querySelector(`[data-message-id="${message.id}"]`);
    if (messageDiv) {
        const contentDiv = messageDiv.querySelector('.message-content');
        contentDiv.innerHTML = escapeHtml(message.content) + ' <span class="edited">(edited)</span>';
    }
}

// Show system message
function showSystemMessage(text) {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) return;

    const systemMsg = document.createElement('div');
    systemMsg.className = 'system-message';
    systemMsg.textContent = text;
    messagesContainer.appendChild(systemMsg);
    scrollToBottom();
}

// Show typing indicator
function showTypingIndicator(userId, isTyping) {
    const indicator = document.getElementById('typing-indicator');
    if (!indicator) return;

    if (isTyping) {
        indicator.querySelector('span').textContent = `User ${userId} is typing...`;
        indicator.style.display = 'block';
    } else {
        indicator.style.display = 'none';
    }
}

// Handle typing
function handleTyping() {
    if (!currentChatRoom || !chatClient) return;

    // Send typing indicator
    chatClient.sendTyping(currentChatRoom.id, true);

    // Clear previous timeout
    if (typingTimeout) {
        clearTimeout(typingTimeout);
    }

    // Stop typing after 3 seconds
    typingTimeout = setTimeout(() => {
        chatClient.sendTyping(currentChatRoom.id, false);
    }, 3000);
}

// Handle key press
function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

// Send message
function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const content = input.value.trim();

    if (!content || !currentChatRoom || !chatClient) return;

    chatClient.sendMessage(currentChatRoom.id, content);
    input.value = '';

    // Stop typing indicator
    if (typingTimeout) {
        clearTimeout(typingTimeout);
        chatClient.sendTyping(currentChatRoom.id, false);
    }
}

// Close chat
function closeChat() {
    if (currentChatRoom && chatClient) {
        chatClient.leaveRoom(currentChatRoom.id);
    }

    currentChatRoom = null;

    const modal = document.getElementById('chat-modal');
    if (modal) {
        modal.remove();
    }
}

// Scroll to bottom
function scrollToBottom() {
    const messagesContainer = document.getElementById('chat-messages');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Make functions globally available
window.openChat = openChat;
window.closeChat = closeChat;
window.sendChatMessage = sendChatMessage;
window.handleChatKeyPress = handleChatKeyPress;
window.handleTyping = handleTyping;
