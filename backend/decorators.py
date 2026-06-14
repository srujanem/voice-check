from functools import wraps
from flask import request, jsonify
from backend.models import User

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header. Please provide a Bearer token."}), 401
        
        api_key = auth_header.split('Bearer ')[1].strip()
        
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({"error": "Invalid API Key. Unauthorized access."}), 401
            
        # Optional: attach user to request context if needed by the route
        request.user = user
        return f(*args, **kwargs)
        
    return decorated_function
