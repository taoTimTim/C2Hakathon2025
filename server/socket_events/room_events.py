from flask_socketio import emit, join_room, leave_room
from flask import request
from services.room_service import RoomService
from socket_events.connection_events import get_user_id_from_socket

def register_handlers(socketio):
    """Register room-related socket event handlers"""

    @socketio.on('join_room')
    def handle_join_room(data):
        """
        Handle user joining a room
        Data: {room_id: int}
        """
        socket_id = request.sid
        user_id = get_user_id_from_socket(socket_id)

        if not user_id:
            emit('error', {'message': 'Unauthorized'})
            return

        room_id = data.get('room_id')

        if not room_id:
            emit('error', {'message': 'room_id is required'})
            return

        try:
            # Verify user is member of room
            room_service = RoomService()
            if not room_service.is_user_in_room(user_id, room_id):
                emit('error', {'message': 'Access denied to this room'})
                return

            # Join SocketIO room
            join_room(f'room_{room_id}')

            # Notify user
            emit('room_joined', {
                'room_id': room_id,
                'message': f'Successfully joined room {room_id}'
            })

            # Notify other users in room
            socketio.emit('user_joined', {
                'user_id': user_id,
                'room_id': room_id
            }, room=f'room_{room_id}', skip_sid=socket_id)

        except Exception as e:
            emit('error', {'message': str(e)})

    @socketio.on('leave_room')
    def handle_leave_room(data):
        """
        Handle user leaving a room
        Data: {room_id: int}
        """
        socket_id = request.sid
        user_id = get_user_id_from_socket(socket_id)

        if not user_id:
            emit('error', {'message': 'Unauthorized'})
            return

        room_id = data.get('room_id')

        if not room_id:
            emit('error', {'message': 'room_id is required'})
            return

        try:
            # Leave SocketIO room
            leave_room(f'room_{room_id}')

            # Notify user
            emit('room_left', {
                'room_id': room_id,
                'message': f'Successfully left room {room_id}'
            })

            # Notify other users in room
            socketio.emit('user_left', {
                'user_id': user_id,
                'room_id': room_id
            }, room=f'room_{room_id}')

        except Exception as e:
            emit('error', {'message': str(e)})
