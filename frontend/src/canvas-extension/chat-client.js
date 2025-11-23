// WebSocket Chat Client using Socket.IO
// Connects to the Flask-SocketIO server

class ChatClient {
    constructor(serverUrl, sessionToken) {
        this.serverUrl = serverUrl;
        this.sessionToken = sessionToken;
        this.socket = null;
        this.currentRoomId = null;
        this.messageHandlers = [];
        this.typingHandlers = [];
        this.userJoinHandlers = [];
        this.userLeaveHandlers = [];
    }

    connect() {
        return new Promise((resolve, reject) => {
            // Load Socket.IO client from CDN
            if (typeof io === 'undefined') {
                const script = document.createElement('script');
                script.src = 'https://cdn.socket.io/4.5.4/socket.io.min.js';
                script.onload = () => this.initializeSocket(resolve, reject);
                script.onerror = () => reject(new Error('Failed to load Socket.IO'));
                document.head.appendChild(script);
            } else {
                this.initializeSocket(resolve, reject);
            }
        });
    }

    initializeSocket(resolve, reject) {
        console.log('Connecting to WebSocket server...');

        this.socket = io(this.serverUrl, {
            auth: {
                token: this.sessionToken
            },
            transports: ['websocket', 'polling']
        });

        this.socket.on('connected', (data) => {
            console.log('Connected to chat server:', data);
            this.setupEventHandlers();
            resolve(data);
        });

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            reject(error);
        });

        this.socket.on('error', (data) => {
            console.error('Socket error:', data.message);
        });
    }

    setupEventHandlers() {
        // Handle incoming messages
        this.socket.on('new_message', (message) => {
            console.log('New message:', message);
            this.messageHandlers.forEach(handler => handler(message));
        });

        // Handle message edits
        this.socket.on('message_edited', (message) => {
            console.log('Message edited:', message);
            this.messageHandlers.forEach(handler => handler(message, true));
        });

        // Handle typing indicators
        this.socket.on('typing_indicator', (data) => {
            this.typingHandlers.forEach(handler => handler(data));
        });

        // Handle user joined
        this.socket.on('user_joined', (data) => {
            console.log('User joined:', data);
            this.userJoinHandlers.forEach(handler => handler(data));
        });

        // Handle user left
        this.socket.on('user_left', (data) => {
            console.log('User left:', data);
            this.userLeaveHandlers.forEach(handler => handler(data));
        });

        // Handle room joined
        this.socket.on('room_joined', (data) => {
            console.log('Joined room:', data);
            this.currentRoomId = data.room_id;
        });

        // Handle room left
        this.socket.on('room_left', (data) => {
            console.log('Left room:', data);
            if (this.currentRoomId === data.room_id) {
                this.currentRoomId = null;
            }
        });
    }

    joinRoom(roomId) {
        if (!this.socket || !this.socket.connected) {
            throw new Error('Not connected to server');
        }

        this.socket.emit('join_room', { room_id: roomId });
    }

    leaveRoom(roomId) {
        if (!this.socket || !this.socket.connected) {
            return;
        }

        this.socket.emit('leave_room', { room_id: roomId });
    }

    sendMessage(roomId, content) {
        if (!this.socket || !this.socket.connected) {
            throw new Error('Not connected to server');
        }

        this.socket.emit('send_message', {
            room_id: roomId,
            content: content
        });
    }

    editMessage(messageId, content) {
        if (!this.socket || !this.socket.connected) {
            throw new Error('Not connected to server');
        }

        this.socket.emit('edit_message', {
            message_id: messageId,
            content: content
        });
    }

    sendTyping(roomId, isTyping) {
        if (!this.socket || !this.socket.connected) {
            return;
        }

        this.socket.emit('typing', {
            room_id: roomId,
            is_typing: isTyping
        });
    }

    onMessage(handler) {
        this.messageHandlers.push(handler);
    }

    onTyping(handler) {
        this.typingHandlers.push(handler);
    }

    onUserJoin(handler) {
        this.userJoinHandlers.push(handler);
    }

    onUserLeave(handler) {
        this.userLeaveHandlers.push(handler);
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
    }

    isConnected() {
        return this.socket && this.socket.connected;
    }
}

// Export for use in other files
window.ChatClient = ChatClient;
