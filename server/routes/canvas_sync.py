from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from services.canvas_api import CanvasAPI

bp = Blueprint('canvas_sync', __name__, url_prefix='/api')

def get_authenticated_user():
    """Helper function to get authenticated user from request"""
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    session_token = auth_header.split(' ')[1]
    auth_service = AuthService()
    user_id = auth_service.validate_session_token(session_token)

    return user_id

@bp.route('/sync', methods=['POST'])
def manual_sync():
    """
    Manually trigger Canvas group sync for authenticated user
    Requires: Authorization header
    Request body: {"canvas_token": "xyz"} (optional, reuse stored token if available)
    """
    user_id = get_authenticated_user()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    canvas_token = data.get('canvas_token')

    if not canvas_token:
        return jsonify({"error": "Canvas API token is required for manual sync"}), 400

    try:
        # Sync Canvas groups
        canvas_api = CanvasAPI(canvas_token)
        result = canvas_api.sync_user_groups(user_id)

        return jsonify({
            "message": "Sync completed successfully",
            "synced_groups": result.get('synced_groups', 0),
            "synced_members": result.get('synced_members', 0)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
