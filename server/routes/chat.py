from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from services.room_service import RoomService
from services.message_service import MessageService

bp = Blueprint('chat', __name__, url_prefix='/api')

def get_authenticated_user():
    """Helper function to get authenticated user from request"""
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    session_token = auth_header.split(' ')[1]
    auth_service = AuthService()
    user_id = auth_service.validate_session_token(session_token)

    return user_id

@bp.route('/rooms', methods=['GET'])
def get_rooms():
    """
    Get all rooms accessible by the authenticated user
    Requires: Authorization header
    """
    user_id = get_authenticated_user()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        room_service = RoomService()
        rooms = room_service.get_user_rooms(user_id)

        return jsonify({"rooms": rooms}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/rooms/<int:room_id>/messages', methods=['GET'])
def get_room_messages(room_id):
    """
    Get message history for a specific room
    Requires: Authorization header
    Query params: limit (default 50), offset (default 0)
    """
    user_id = get_authenticated_user()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Verify user has access to this room
        room_service = RoomService()
        if not room_service.is_user_in_room(user_id, room_id):
            return jsonify({"error": "Access denied to this room"}), 403

        # Get messages
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        message_service = MessageService()
        messages = message_service.get_room_messages(room_id, limit, offset)

        return jsonify({"messages": messages}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/users/me', methods=['GET'])
def get_current_user():
    """
    Get current authenticated user info
    Requires: Authorization header
    """
    user_id = get_authenticated_user()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        from services.user_service import UserService
        user_service = UserService()
        user = user_service.get_user_by_id(user_id)

        return jsonify({"user": user}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
