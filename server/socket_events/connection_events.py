from flask_socketio import emit, disconnect
from services.auth_service import AuthService
from services.user_service import UserService
from datetime import datetime

# Store active socket connections: {socket_id: user_id}
active_connections = {}

def register_handlers(socketio):
    """Register connection-related socket event handlers"""

    @socketio.on('connect')
    def handle_connect(auth):
        """
        Handle new socket connection
        Client must provide: {token: "session_token"}
        """
        if not auth or 'token' not in auth:
            print("Connection rejected: No authentication token provided")
            disconnect()
            return False

        session_token = auth['token']

        try:
            # Validate session token
            auth_service = AuthService()
            user_id = auth_service.validate_session_token(session_token)

            if not user_id:
                print("Connection rejected: Invalid session token")
                disconnect()
                return False

            # Store connection
            from flask import request
            socket_id = request.sid
            active_connections[socket_id] = user_id

            # Update user's last_seen
            user_service = UserService()
            user_service.update_last_seen(user_id)

            print(f"User {user_id} connected with socket {socket_id}")

            emit('connected', {
                'message': 'Successfully connected to chat server',
                'user_id': user_id
            })

            return True

        except Exception as e:
            print(f"Connection error: {str(e)}")
            disconnect()
            return False

    @socketio.on('disconnect')
    def handle_disconnect():
        """
        Handle socket disconnection
        Update user's last_seen timestamp
        """
        from flask import request
        socket_id = request.sid

        if socket_id in active_connections:
            user_id = active_connections[socket_id]

            try:
                # Update user's last_seen
                user_service = UserService()
                user_service.update_last_seen(user_id)

                print(f"User {user_id} disconnected")

            except Exception as e:
                print(f"Disconnect error: {str(e)}")

            finally:
                del active_connections[socket_id]

    @socketio.on('ping')
    def handle_ping():
        """
        Handle ping for keeping connection alive
        """
        emit('pong', {'timestamp': datetime.utcnow().isoformat()})

def get_user_id_from_socket(socket_id):
    """Helper function to get user_id from socket_id"""
    return active_connections.get(socket_id)
