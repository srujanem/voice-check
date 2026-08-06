from flask import Blueprint, request, jsonify
from backend.services.external_db import external_db
from backend.decorators import require_api_key
from datetime import datetime
import uuid

history_bp = Blueprint('history', __name__)

@history_bp.route("/history", methods=["POST"])
@require_api_key
def save_history():
    data = request.json
    scan_type = data.get("scan_type")
    target_name = data.get("target_name")
    is_ai = data.get("is_ai")
    confidence = data.get("confidence")
    user_id = request.user['uid']

    # Require a real logged-in user
    if user_id == 'guest':
        return jsonify({"error": "Login required to save history"}), 401

    if not scan_type or not target_name:
        return jsonify({"error": "Missing required fields"}), 400
        
    scan_data = {
        "id": str(uuid.uuid4()),
        "scan_type": scan_type,
        "target_name": target_name,
        "is_ai": is_ai,
        "confidence": confidence,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    collection_name = f"history_{user_id}"
    result = external_db.create_document(collection_name, scan_data)
    
    if result.get("success"):
        return jsonify({"message": "Scan saved", "id": scan_data["id"]})
    return jsonify({"error": "Failed to save history"}), 500

@history_bp.route("/history", methods=["GET"])
@require_api_key
def get_history():
    user_id = request.user['uid']
        
    try:
        collection_name = f"history_{user_id}"
        result = external_db.list_documents(collection_name)
        
        if result.get("success"):
            docs = result.get("data", [])
            # Sort by timestamp descending
            docs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return jsonify(docs[:50])
            
        return jsonify([])
    except Exception as e:
        print(f"External DB history error: {e}")
        return jsonify([])
