from functools import wraps
from flask import request, jsonify
from firebase_admin import auth

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header. Please provide a Bearer token."}), 401
        
        id_token = auth_header.split('Bearer ')[1].strip()
        
        try:
            decoded_token = auth.verify_id_token(id_token)
            request.user = decoded_token  # Contains 'uid', 'email', etc.
        except Exception as e:
            return jsonify({"error": f"Invalid API Key. Unauthorized access. ({str(e)})"}), 401
            
        return f(*args, **kwargs)
        
    return decorated_function
