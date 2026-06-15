from flask import Blueprint, request, jsonify
from backend.firebase_init import get_db
from backend.decorators import require_api_key
from datetime import datetime
from firebase_admin import firestore

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
    
    if not scan_type or not target_name:
        return jsonify({"error": "Missing required fields"}), 400
        
    db = get_db()
    
    doc_ref = db.collection('users').document(user_id).collection('history').document()
    scan_data = {
        "id": doc_ref.id,
        "scan_type": scan_type,
        "target_name": target_name,
        "is_ai": is_ai,
        "confidence": confidence,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    doc_ref.set(scan_data)
    
    return jsonify({"message": "Scan saved", "id": doc_ref.id})

@history_bp.route("/history", methods=["GET"])
@require_api_key
def get_history():
    user_id = request.user['uid']
        
    db = get_db()
    
    try:
        scans_ref = db.collection('users').document(user_id).collection('history')
        docs = scans_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(50).stream()
        
        results = []
        for doc in docs:
            s = doc.to_dict()
            # Firestore timestamp to string
            ts = s.get("timestamp")
            if ts:
                ts_str = ts.isoformat()
            else:
                ts_str = None
                
            results.append({
                "id": s.get("id"),
                "scan_type": s.get("scan_type"),
                "target_name": s.get("target_name"),
                "is_ai": s.get("is_ai"),
                "confidence": s.get("confidence"),
                "timestamp": ts_str
            })
        return jsonify(results)
    except Exception as e:
        print(f"Firestore history error: {e}")
        return jsonify([])
