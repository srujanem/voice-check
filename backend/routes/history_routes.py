from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models import ScanHistory

history_bp = Blueprint('history', __name__)

@history_bp.route("/history", methods=["POST"])
def save_history():
    data = request.json
    scan_type = data.get("scan_type")
    target_name = data.get("target_name")
    is_ai = data.get("is_ai")
    confidence = data.get("confidence")
    user_id = data.get("user_id") # optional for now
    
    if not scan_type or not target_name:
        return jsonify({"error": "Missing required fields"}), 400
        
    new_scan = ScanHistory(
        user_id=user_id,
        scan_type=scan_type,
        target_name=target_name,
        is_ai=is_ai,
        confidence=confidence
    )
    db.session.add(new_scan)
    db.session.commit()
    
    return jsonify({"message": "Scan saved", "id": new_scan.id})

@history_bp.route("/history", methods=["GET"])
def get_history():
    user_id = request.args.get("user_id")
    query = ScanHistory.query
    if user_id:
        query = query.filter_by(user_id=user_id)
        
    scans = query.order_by(ScanHistory.timestamp.desc()).limit(50).all()
    results = []
    for s in scans:
        results.append({
            "id": s.id,
            "scan_type": s.scan_type,
            "target_name": s.target_name,
            "is_ai": s.is_ai,
            "confidence": s.confidence,
            "timestamp": s.timestamp.isoformat()
        })
    return jsonify(results)
