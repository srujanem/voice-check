from flask import Blueprint, request, jsonify
from backend.decorators import require_api_key
from backend.services.external_db import ExternalDB, external_db as _external_db

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
    data = request.json
    base_url = data.get("base_url")
    api_key = data.get("api_key")

    if not base_url or not api_key:
        return jsonify({"error": "base_url and api_key are required"}), 400

    new_db = ExternalDB(base_url, api_key)
    
    # Test connection by listing a dummy collection
    test = new_db.list_documents("system_test_conn")
    if test["success"] or test.get("status_code") in [200, 404]:
        _db_ref["instance"] = new_db
        return jsonify({
            "message": "External DB connected successfully",
            "resolved_url": new_db.base_url
        }), 200
    else:
        return jsonify({
            "error": "Failed to connect to the external DB",
            "details": test.get("details", test.get("error"))
        }), 400


# ------------------------------------------------------------------
# GET /api/external/status
# ------------------------------------------------------------------
@external_db_bp.route("/api/external/status", methods=["GET"])
def external_db_status():
    """Return connection status for the external database."""
    db = _get_db()
    
    if not db.is_configured():
        return jsonify({"configured": False}), 200

    test = db.list_documents("system_test_conn")
    if test["success"] or test.get("status_code") in [200, 404]:
        return jsonify({
            "configured": True,
            "base_url": db.base_url,
            "connection_test": "ok",
        }), 200

    return jsonify({
        "configured": True,
        "base_url": db.base_url,
        "connection_test": "failed",
        "details": test.get("details", test.get("error")),
    }), 200


# ------------------------------------------------------------------
# GET /api/external/collections/<collection>
# ------------------------------------------------------------------
@external_db_bp.route("/api/external/collections/<collection>", methods=["GET"])
def list_collection(collection):
    """Proxy: list documents from the external DB."""
    db = _get_db()
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
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    result = db.create_document(collection, data)
    if result["success"]:
        return jsonify(result["data"]), result.get("status_code", 201)
    return jsonify({"error": result.get("error"), "details": result.get("details")}), 502
