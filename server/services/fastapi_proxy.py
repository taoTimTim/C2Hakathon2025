import requests
from flask import request
import os

class FastAPIProxy:
    """Proxy service to forward requests to FastAPI backend"""

    def __init__(self):
        self.fastapi_url = os.getenv('FASTAPI_URL', 'http://localhost:8000')

    def forward_request(self, endpoint, method='GET', json_data=None, query_params=None):
        """
        Forward request to FastAPI backend

        Args:
            endpoint: FastAPI endpoint (e.g., '/rooms/123/messages')
            method: HTTP method (GET, POST, PUT, DELETE)
            json_data: JSON body for POST/PUT requests
            query_params: Query parameters dict

        Returns:
            (response_json, status_code)
        """
        url = f"{self.fastapi_url}{endpoint}"

        # Forward authorization header if present
        headers = {}
        if request.headers.get('Authorization'):
            headers['Authorization'] = request.headers.get('Authorization')

        try:
            print(f"[PROXY] {method} {url} | params: {query_params}")

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

            print(f"[PROXY] Response: {response.status_code}")

            # Return response and status code
            try:
                return response.json(), response.status_code
            except:
                return {"message": response.text}, response.status_code

        except requests.exceptions.ConnectionError:
            return {"error": "FastAPI backend is not reachable"}, 503
        except Exception as e:
            return {"error": str(e)}, 500
