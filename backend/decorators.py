from functools import wraps
from flask import request, jsonify, current_app
import jwt

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Login removed as requested; bypass auth completely.
        request.user = {'uid': 'local_user'}
        return f(*args, **kwargs)
        
    return decorated_function
