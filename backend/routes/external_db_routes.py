from flask import Blueprint, request, jsonify
from backend.decorators import require_api_key
from backend.firebase_init import get_db
from backend.services.external_db import ExternalDB, external_db as _external_db
from firebase_admin import firestore

external_db_bp = Blueprint("external_db", __name__)

# Keep a mutable reference so /connect can swap the instance at runtime.
_db_ref = {"instance": _external_db}


def _get_db():
    """Return the current ExternalDB instance."""
    return _db_ref["instance"]


# ------------------------------------------------------------------
# POST /api/external/connect
# ------------------------------------------------------------------
@external_db_bp.route("/api/external/connect", methods=["POST"])
def connect_external_db():
    """Accept base_url + api_key, reinitialise the ExternalDB singleton."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    base_url = data.get("base_url")
    api_key = data.get("api_key")

    if not base_url or not api_key:
        return jsonify({"error": "Both 'base_url' and 'api_key' are required"}), 400

    new_instance = ExternalDB(base_url=base_url, api_key=api_key)

    # Quick connectivity test
    test = new_instance.list_documents("_ping")
    if not test["success"] and "Could not connect" in test.get("error", ""):
        return jsonify({
            "error": "Could not reach the external database",
            "details": test.get("error"),
        }), 502

    _db_ref["instance"] = new_instance

    return jsonify({
        "message": "External DB connected successfully",
        "resolved_url": new_instance.base_url
    }), 200


# ------------------------------------------------------------------
# GET /api/external/status
# ------------------------------------------------------------------
@external_db_bp.route("/api/external/status", methods=["GET"])
def external_db_status():
    """Return connection status for the external database."""
    db = _get_db()
    configured = db.is_configured()

    masked_url = None
    if db.base_url:
        # Show scheme + first 12 chars then mask the rest
        visible = db.base_url[:min(len(db.base_url), 20)]
        masked_url = visible + "****" if len(db.base_url) > 20 else db.base_url

    test_result = None
    if configured:
        test = db.list_documents("_ping")
        test_result = "ok" if test["success"] else test.get("error")

    return jsonify({
        "configured": configured,
        "base_url": masked_url,
        "connection_test": test_result,
    }), 200


# ------------------------------------------------------------------
# POST /api/external/sync-history
# ------------------------------------------------------------------
@external_db_bp.route("/api/external/sync-history", methods=["POST"])
@require_api_key
def sync_history():
    """Read the user's scan history from Firebase and push it to the
    external DB's ``scan_history`` collection."""
    db = _get_db()
    if not db.is_configured():
        return jsonify({"error": "External DB is not configured. Use /api/external/connect first."}), 400

    user_id = request.user["uid"]

    try:
        fb = get_db()
        scans_ref = fb.collection("users").document(user_id).collection("history")
        docs = scans_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).stream()

        synced = 0
        errors = 0
        for doc in docs:
            record = doc.to_dict()
            # Convert Firestore timestamps to ISO strings for JSON compat
            ts = record.get("timestamp")
            if ts:
                record["timestamp"] = ts.isoformat()
            record["firebase_uid"] = user_id

            result = db.create_document("scan_history", record)
            if result["success"]:
                synced += 1
            else:
                errors += 1

        return jsonify({
            "message": "History sync complete",
            "synced": synced,
            "errors": errors,
        }), 200

    except Exception as e:
        print(f"sync-history error: {e}")
        return jsonify({"error": f"Failed to sync history: {str(e)}"}), 500


# ------------------------------------------------------------------
# GET /api/external/collections/<collection>
# ------------------------------------------------------------------
@external_db_bp.route("/api/external/collections/<collection>", methods=["GET"])
def list_collection(collection):
    """Proxy: list documents from the external DB."""
    db = _get_db()
    if not db.is_configured():
        return jsonify({"error": "External DB is not configured. Use /api/external/connect first."}), 400

    result = db.list_documents(collection)
    if result["success"]:
        return jsonify(result["data"]), result.get("status_code", 200)
    return jsonify({"error": result.get("error"), "details": result.get("details")}), 502


# ------------------------------------------------------------------
# POST /api/external/collections/<collection>
# ------------------------------------------------------------------
@external_db_bp.route("/api/external/collections/<collection>", methods=["POST"])
def create_in_collection(collection):
    """Proxy: create a document in the external DB."""
    db = _get_db()
    if not db.is_configured():
        return jsonify({"error": "External DB is not configured. Use /api/external/connect first."}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    result = db.create_document(collection, data)
    if result["success"]:
        return jsonify(result["data"]), result.get("status_code", 201)
    return jsonify({"error": result.get("error"), "details": result.get("details")}), 502
