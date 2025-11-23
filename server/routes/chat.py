from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from services.fastapi_proxy import FastAPIProxy

bp = Blueprint('chat', __name__, url_prefix='/api')
proxy = FastAPIProxy()

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
    Proxy to FastAPI: Get all rooms accessible by the authenticated user
    Requires: Authorization header
    """
    user_id = get_authenticated_user()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Forward to FastAPI with user_id query param
    response, status_code = proxy.forward_request('/rooms', method='GET', query_params={'user_id': user_id})
    return jsonify(response), status_code

@bp.route('/rooms/<int:room_id>/messages', methods=['GET'])
def get_room_messages(room_id):
    """
    Proxy to FastAPI: Get message history for a specific room
    Requires: Authorization header
    Query params: limit (default 50), offset (default 0)
    """
    user_id = get_authenticated_user()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Forward query params
    query_params = {
        'limit': request.args.get('limit', 50, type=int),
        'offset': request.args.get('offset', 0, type=int)
    }

    # Forward to FastAPI
    response, status_code = proxy.forward_request(
        f'/rooms/{room_id}/messages',
        method='GET',
        query_params=query_params
    )
    return jsonify(response), status_code

@bp.route('/users/me', methods=['GET'])
def get_current_user():
    """
    Proxy to FastAPI: Get current authenticated user info
    Requires: Authorization header
    """
    user_id = get_authenticated_user()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Forward to FastAPI (use /users/{user_id} endpoint)
    response, status_code = proxy.forward_request(f'/users/{user_id}', method='GET')
    return jsonify(response), status_code

# Additional proxy routes for FastAPI endpoints
@bp.route('/groups', methods=['GET'])
def get_groups():
    """Proxy to FastAPI: Get all groups"""
    user_id = get_authenticated_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    response, status_code = proxy.forward_request('/groups', method='GET', query_params={'user_id': user_id})
    return jsonify(response), status_code

@bp.route('/groups/<int:group_id>/join', methods=['POST'])
def join_group(group_id):
    """Proxy to FastAPI: Join a group"""
    user_id = get_authenticated_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Forward request body with user_id
    json_data = request.get_json() or {}
    json_data['user_id'] = user_id
    
    response, status_code = proxy.forward_request(
        f'/groups/{group_id}/join',
        method='POST',
        json_data=json_data
    )
    return jsonify(response), status_code

@bp.route('/clubs', methods=['GET'])
def get_clubs():
    """Proxy to FastAPI: Get all clubs"""
    user_id = get_authenticated_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    response, status_code = proxy.forward_request('/clubs', method='GET')
    return jsonify(response), status_code

@bp.route('/classes', methods=['GET'])
def get_classes():
    """Proxy to FastAPI: Get all classes"""
    user_id = get_authenticated_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    response, status_code = proxy.forward_request('/classes', method='GET', query_params={'user_id': user_id})
    return jsonify(response), status_code

@bp.route('/posts', methods=['GET', 'POST'])
def posts():
    """Proxy to FastAPI: Get or create posts"""
    user_id = get_authenticated_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        response, status_code = proxy.forward_request('/posts', method='GET')
    else:  # POST
        response, status_code = proxy.forward_request('/posts', method='POST', json_data=request.get_json())

    return jsonify(response), status_code
