from flask_socketio import emit, join_room, leave_room
from flask import request
from services.message_service import MessageService
from services.room_service import RoomService
from socket_events.connection_events import get_user_id_from_socket
from datetime import datetime

def register_handlers(socketio):
    """Register message-related socket event handlers"""

    @socketio.on('send_message')
    def handle_send_message(data):
        """
        Handle new message from client
        Data: {room_id: int, content: string}
        """
        socket_id = request.sid
        user_id = get_user_id_from_socket(socket_id)

        if not user_id:
            emit('error', {'message': 'Unauthorized'})
            return

        room_id = data.get('room_id')
        content = data.get('content')

        if not room_id or not content:
            emit('error', {'message': 'room_id and content are required'})
            return

        try:
            # Verify user is in room
            room_service = RoomService()
            if not room_service.is_user_in_room(user_id, room_id):
                emit('error', {'message': 'Access denied to this room'})
                return

            # Save message to database
            message_service = MessageService()
            message = message_service.create_message(user_id, room_id, content)

            # Broadcast message to all users in room
            socketio.emit('new_message', message, room=f'room_{room_id}')

        except Exception as e:
            emit('error', {'message': str(e)})

    @socketio.on('edit_message')
    def handle_edit_message(data):
        """
        Handle message edit
        Data: {message_id: int, content: string}
        """
        socket_id = request.sid
        user_id = get_user_id_from_socket(socket_id)

        if not user_id:
            emit('error', {'message': 'Unauthorized'})
            return

        message_id = data.get('message_id')
        content = data.get('content')

        if not message_id or not content:
            emit('error', {'message': 'message_id and content are required'})
            return

        try:
            message_service = MessageService()

            # Verify user owns the message
            original_message = message_service.get_message_by_id(message_id)
            if not original_message or original_message['user_id'] != user_id:
                emit('error', {'message': 'You can only edit your own messages'})
                return

            # Update message
            updated_message = message_service.edit_message(message_id, content)

            # Broadcast edit to all users in room
            room_id = original_message['room_id']
            socketio.emit('message_edited', updated_message, room=f'room_{room_id}')

        except Exception as e:
            emit('error', {'message': str(e)})

    @socketio.on('typing')
    def handle_typing(data):
        """
        Handle typing indicator
        Data: {room_id: int, is_typing: bool}
        """
        socket_id = request.sid
        user_id = get_user_id_from_socket(socket_id)

        if not user_id:
            return

        room_id = data.get('room_id')
        is_typing = data.get('is_typing', False)

        if not room_id:
            return

        try:
            # Verify user is in room
            room_service = RoomService()
            if not room_service.is_user_in_room(user_id, room_id):
                return

            # Broadcast typing indicator to room (excluding sender)
            socketio.emit('typing_indicator', {
                'user_id': user_id,
                'room_id': room_id,
                'is_typing': is_typing
            }, room=f'room_{room_id}', skip_sid=socket_id)

        except Exception as e:
            print(f"Typing indicator error: {str(e)}")
