// HTTP Polling Chat Client (CSP-safe, no WebSocket required)
// Uses periodic polling to check for new messages

class ChatClient {
    constructor(serverUrl, sessionToken) {
        this.serverUrl = serverUrl;
        this.sessionToken = sessionToken;
        this.connected = false;
        this.currentRoomId = null;
        this.messageHandlers = [];
        this.pollingInterval = null;
        this.lastMessageIdByRoom = {}; // Track last message ID per room
        this.POLL_INTERVAL = 1000; // Poll every 1 second
    }

    async connect() {
        // Test connection by trying to get user info
        try {
            console.log('Testing connection to server...');
            const response = await window.safeFetch(`${this.serverUrl}/api/users/me`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.sessionToken}`,
                    'Content-Type': 'application/json'
                }
            });

            console.log('Connected to server:', response);
            this.connected = true;
            return { status: 'connected', user: response };
        } catch (error) {
            console.error('Connection failed:', error);
            this.connected = false;
            throw error;
        }
    }

    joinRoom(roomId) {
        if (!this.connected) {
            console.error('Cannot join room: Not connected');
            return;
        }

        console.log('Joining room:', roomId);

        // Stop polling previous room if any
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }

        this.currentRoomId = roomId;

        // Initialize tracking for this room if not already done
        if (!(roomId in this.lastMessageIdByRoom)) {
            this.lastMessageIdByRoom[roomId] = null;
        }

        // Start polling for new messages
        this.startPolling();
    }

    leaveRoom(roomId) {
        console.log('Leaving room:', roomId);

        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }

        if (this.currentRoomId === roomId) {
            this.currentRoomId = null;
        }
    }

    startPolling() {
        // Initial poll
        this.pollMessages();

        // Poll every 1 second
        this.pollingInterval = setInterval(() => {
            this.pollMessages();
        }, this.POLL_INTERVAL);
    }

    async pollMessages() {
        if (!this.currentRoomId || !this.connected) {
            return;
        }

        try {
            // Fetch recent messages
            const messages = await window.safeFetch(
                `${this.serverUrl}/api/rooms/${this.currentRoomId}/messages?limit=50`,
                {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${this.sessionToken}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (!Array.isArray(messages) || messages.length === 0) {
                return;
            }

            // Sort messages by ID to ensure correct order
            messages.sort((a, b) => a.id - b.id);

            // Get the latest message ID
            const latestMessageId = messages[messages.length - 1].id;

            // Get the last message ID for this specific room
            const lastSeenId = this.lastMessageIdByRoom[this.currentRoomId];

            // If this is first poll for this room, just set the last message ID
            if (lastSeenId === null) {
                this.lastMessageIdByRoom[this.currentRoomId] = latestMessageId;
                return;
            }

            // Check for new messages (sorted by ID)
            const newMessages = messages.filter(msg => msg.id > lastSeenId);

            if (newMessages.length > 0) {
                // Notify handlers about new messages (already sorted)
                newMessages.forEach(message => {
                    this.messageHandlers.forEach(handler => handler(message, false));
                });

                // Update last message ID for this room
                this.lastMessageIdByRoom[this.currentRoomId] = latestMessageId;
            }

        } catch (error) {
            console.error('Error polling messages:', error);
        }
    }

    async sendMessage(roomId, content) {
        if (!this.connected) {
            console.error('Cannot send message: Not connected');
            return;
        }

        console.log('Sending message to room:', roomId);

        try {
            // Use background script to send message
            const message = await window.safeFetch(
                `${this.serverUrl}/api/rooms/${roomId}/messages`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.sessionToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ content })
                }
            );

            console.log('Message sent:', message);

            // Immediately poll for the new message
            setTimeout(() => this.pollMessages(), 100);

        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }

    sendTyping(roomId, isTyping) {
        // Typing indicators not supported in polling mode
        // Could implement by sending API requests, but skipping for simplicity
    }

    onMessage(handler) {
        this.messageHandlers.push(handler);
    }

    onTyping(handler) {
        // Not supported in polling mode
    }

    onUserJoin(handler) {
        // Not supported in polling mode
    }

    onUserLeave(handler) {
        // Not supported in polling mode
    }

    disconnect() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
        this.connected = false;
        this.currentRoomId = null;
        // Keep lastMessageIdByRoom to maintain state across reconnects
    }
}

// Make ChatClient available globally
window.ChatClient = ChatClient;
