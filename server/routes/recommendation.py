from flask import Blueprint, request, jsonify
from services.recommendation_proxy import RecommendationProxy

bp = Blueprint('recommendation', __name__)
proxy = RecommendationProxy()

@bp.route('/recommend', methods=['POST', 'OPTIONS'])
def recommend():
    """Proxy /recommend endpoint to recommendation service"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    json_data = request.get_json()
    result, status_code = proxy.forward_request('/recommend', method='POST', json_data=json_data)
    return jsonify(result), status_code

@bp.route('/items', methods=['GET', 'OPTIONS'])
def get_items():
    """Proxy /items endpoint to recommendation service"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    result, status_code = proxy.forward_request('/items', method='GET')
    return jsonify(result), status_code

