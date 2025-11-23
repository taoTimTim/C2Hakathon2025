from flask import Blueprint, request, jsonify
from services.canvas_api import CanvasAPI
from services.auth_service import AuthService
from services.user_service import UserService

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user with Canvas API token
    Request body: {"canvas_token": "xyz"}
    Returns: {"session_token": "abc", "user": {...}}
    """
    data = request.get_json()
    canvas_token = data.get('canvas_token')

    if not canvas_token:
        return jsonify({"error": "Canvas API token is required"}), 400

    try:
        # Validate token and get user info from Canvas
        canvas_api = CanvasAPI(canvas_token)
        user_info = canvas_api.get_user_info()

        if not user_info:
            return jsonify({"error": "Invalid Canvas API token. Please check that your token is correct."}), 401

        # Create or update user in database
        user_service = UserService()
        user = user_service.create_or_update_user(user_info)

        # Generate session token using canvas_user_id
        auth_service = AuthService()
        session_token = auth_service.generate_session_token(user['canvas_user_id'])

        # Sync Canvas groups to rooms (in background if possible)
        try:
            canvas_api.sync_user_groups(user['canvas_user_id'])
        except Exception as sync_error:
            print(f"Warning: Group sync failed: {sync_error}")
            # Continue even if sync fails

        return jsonify({
            "session_token": session_token,
            "user": user
        }), 200

    except KeyError as e:
        print(f"KeyError in login: {str(e)}")
        return jsonify({"error": f"Missing required field: {str(e)}"}), 500
    except Exception as e:
        # The Canvas API now provides detailed error messages
        error_message = str(e)
        print(f"Login error: {error_message}")
        import traceback
        traceback.print_exc()
        
        # Determine appropriate status code based on error message
        status_code = 500
        if "Invalid Canvas API token" in error_message or "401" in error_message:
            status_code = 401
        elif "Access forbidden" in error_message or "403" in error_message:
            status_code = 403
        elif "Could not connect" in error_message or "Connection" in error_message:
            status_code = 503  # Service Unavailable
        
        return jsonify({"error": error_message}), status_code

@bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout user by invalidating session token
    Requires: Authorization header with session token
    """
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid authorization header"}), 401

    session_token = auth_header.split(' ')[1]

    try:
        auth_service = AuthService()
        auth_service.invalidate_session_token(session_token)

        return jsonify({"message": "Logged out successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/verify', methods=['GET'])
def verify():
    """
    Verify session token and return user info
    Requires: Authorization header with session token
    """
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid authorization header"}), 401

    session_token = auth_header.split(' ')[1]

    try:
        auth_service = AuthService()
        user_id = auth_service.validate_session_token(session_token)

        if not user_id:
            return jsonify({"error": "Invalid or expired session token"}), 401

        user_service = UserService()
        user = user_service.get_user_by_id(user_id)

        return jsonify({"user": user}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
