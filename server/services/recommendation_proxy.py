import requests
from flask import request
import os

class RecommendationProxy:
    """Proxy service to forward requests to recommendation service"""

    def __init__(self):
        self.recommendation_url = os.getenv('RECOMMENDATION_URL', 'http://localhost:5001')

    def forward_request(self, endpoint, method='GET', json_data=None, query_params=None):
        """
        Forward request to recommendation service

        Args:
            endpoint: Recommendation endpoint (e.g., '/recommend', '/items')
            method: HTTP method (GET, POST, PUT, DELETE)
            json_data: JSON body for POST/PUT requests
            query_params: Query parameters dict

        Returns:
            (response_json, status_code)
        """
        url = f"{self.recommendation_url}{endpoint}"

        # Forward headers
        headers = {'Content-Type': 'application/json'}
        if request.headers.get('Authorization'):
            headers['Authorization'] = request.headers.get('Authorization')

        try:
            print(f"[RECOMMENDATION PROXY] {method} {url} | params: {query_params}")

            if method == 'GET':
                response = requests.get(url, headers=headers, params=query_params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=json_data, params=query_params)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=json_data, params=query_params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=query_params)
            else:
                return {"error": f"Unsupported method: {method}"}, 400

            print(f"[RECOMMENDATION PROXY] Response: {response.status_code}")

            # Return response and status code
            try:
                return response.json(), response.status_code
            except:
                return {"message": response.text}, response.status_code

        except requests.exceptions.ConnectionError:
            return {"error": "Recommendation service is not reachable"}, 503
        except Exception as e:
            return {"error": str(e)}, 500

