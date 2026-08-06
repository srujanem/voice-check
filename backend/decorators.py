from functools import wraps
from flask import request, jsonify, current_app
import jwt


def require_api_key(f):
    """
    Decorator that:
    - Accepts an optional 'Authorization: Bearer <jwt>' header.
    - If the token is valid, decodes it and sets request.user with the real
      email and a stable uid derived from the email (sha-256 hex, first 16 chars).
    - If no token / invalid token, falls back to an anonymous guest user so
      that public endpoints still work without authentication.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import hashlib

        # Defaults for unauthenticated / anonymous access
        user_email = "guest@voicecheck.app"
        user_uid   = "guest"

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            try:
                decoded = jwt.decode(
                    token,
                    current_app.config["SECRET_KEY"],
                    algorithms=["HS256"]
                )
                email = decoded.get("email", "").strip().lower()
                if email:
                    user_email = email
                    # Stable, URL-safe uid derived from the email
                    user_uid = hashlib.sha256(email.encode()).hexdigest()[:24]
            except jwt.ExpiredSignatureError:
                # Token expired — treat as guest (or you could return 401)
                pass
            except Exception:
                pass  # Malformed token — fall through to guest

        request.user = {"uid": user_uid, "email": user_email}
        return f(*args, **kwargs)

    return decorated_function
