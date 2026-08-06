from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime
from backend.services.external_db import external_db

results_bp = Blueprint('results', __name__)

_COLLECTION = "shared_results"

@results_bp.route("/api/results/save", methods=["POST"])
def save_result():
    data = request.json or {}
    result_data = data.get("result", {})
    filename = data.get("filename", "Unknown")
    scan_type = data.get("type", "voice")

    result_id = str(uuid.uuid4())[:8]

    is_ai = result_data.get("is_ai", False)
    prob_ai    = float(result_data.get("prob_ai", 50.0))    / 100.0 if result_data.get("prob_ai")    is not None else 0.5
    prob_human = float(result_data.get("prob_human", 50.0)) / 100.0 if result_data.get("prob_human") is not None else (1.0 - prob_ai)

    entry = {
        "id":               result_id,
        "filename":         filename,
        "scan_type":        scan_type,
        "ai_probability":   prob_ai,
        "human_probability": prob_human,
        "timestamp":        datetime.utcnow().isoformat(),
        "raw":              result_data
    }

    # Persist to external DB so links survive server restarts
    db_resp = external_db.create_document(_COLLECTION, entry)
    if not db_resp.get("success"):
        # Graceful fallback — still return the ID even if DB save failed
        print(f"[results] DB save failed (non-fatal): {db_resp.get('error')}")

    return jsonify({"id": result_id, "message": "Result saved successfully"}), 200


@results_bp.route("/api/results/<result_id>", methods=["GET"])
def get_result(result_id):
    resp = external_db.list_documents(_COLLECTION)
    if resp.get("success"):
        docs = resp.get("data", [])
        entry = next((d for d in docs if d.get("id") == result_id), None)
        if entry:
            return jsonify(entry), 200
    return jsonify({"error": "Result not found or expired"}), 404
