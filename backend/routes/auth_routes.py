from flask import Blueprint, request, jsonify, current_app
import random
import datetime
import jwt
from backend.services.external_db import external_db

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/api/auth/request-otp", methods=["POST"])
def request_otp():
    """Proxy for /api/db/auth/signup to send OTP to a new user."""
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    resp = external_db._request("POST", "/api/db/auth/signup", json_body={"email": email})
    
    if not resp.get("success", True) and "error" in resp: # Assume success if no "success" key, but error key exists means failure
        print(f"DB Error: {resp.get('error')}")
        return jsonify({"error": f"Database error: {resp.get('error')} - Please ensure the VK server is online."}), 500
        
    return jsonify({"message": "OTP generated."}), 200


@auth_bp.route("/api/auth/verify-otp", methods=["POST"])
def verify_otp():
    """Proxy for /api/db/auth/verify to create account."""
    data = request.json
    email = data.get("email")
    otp = data.get("otp")
    password = data.get("password")
    
    if not email or not otp or not password:
        return jsonify({"error": "Email, OTP, and password are required"}), 400
        
    resp = external_db._request("POST", "/api/db/auth/verify", json_body={
        "email": email,
        "otp": str(otp),
        "password": password
    })
    
    if "error" in resp and not resp.get("success", True):
        return jsonify({"error": f"Verification failed: {resp.get('error', 'Invalid OTP')}"}), 401
        
    token = jwt.encode({
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, current_app.config["SECRET_KEY"], algorithm="HS256")
        
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {"email": email}
    }), 200


@auth_bp.route("/api/auth/login", methods=["POST"])
def login_password():
    """Proxy for /api/db/auth/login to authenticate existing user."""
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
        
    resp = external_db._request("POST", "/api/db/auth/login", json_body={
        "email": email,
        "password": password
    })
    
    if "error" in resp and not resp.get("success", True):
        return jsonify({"error": f"Login failed: {resp.get('error', 'Invalid credentials')}"}), 401
        
    token = jwt.encode({
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, current_app.config["SECRET_KEY"], algorithm="HS256")
        
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {"email": email}
    }), 200
