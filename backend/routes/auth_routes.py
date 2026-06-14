from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models import User
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400
        
    api_key = f"vc_live_{uuid.uuid4().hex}"
    new_user = User(email=email, password_hash=password, api_key=api_key)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User created", "api_key": api_key, "user_id": new_user.id})

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    user = User.query.filter_by(email=email).first()
    if user and user.password_hash == password:
        return jsonify({"message": "Login successful", "api_key": user.api_key, "user_id": user.id})
        
    return jsonify({"error": "Invalid credentials"}), 401
