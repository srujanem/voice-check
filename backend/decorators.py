from functools import wraps
from flask import request, jsonify, current_app
import jwt

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_email = 'srujanem222@gmail.com'
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                decoded = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
                user_email = decoded.get('email', user_email)
            except Exception:
                pass
        request.user = {'uid': 'local_user', 'email': user_email}
        return f(*args, **kwargs)
        
    return decorated_function
