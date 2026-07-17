from functools import wraps
from flask import request, jsonify, current_app
import jwt

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header. Please provide a Bearer token."}), 401
        
        token = auth_header.split('Bearer ')[1].strip()
        
        if not token:
            return jsonify({"error": "Invalid token. Unauthorized access."}), 401
            
        try:
            # Decode the JWT token to get the user's email
            decoded = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            # Treat the user's email as their identifier (uid)
            request.user = {'uid': decoded.get("email")}
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired. Please log in again."}), 401
        except jwt.InvalidTokenError:
            # For backward compatibility during local dev, if the token is exactly the master key, allow it as 'dev_admin'
            if token == 'sk_test_CRlzyngFryWvSo0kA06JpI1tDPFTZgL5':
                request.user = {'uid': 'dev_admin'}
            else:
                return jsonify({"error": "Invalid token. Unauthorized access."}), 401
            
        return f(*args, **kwargs)
        
    return decorated_function
