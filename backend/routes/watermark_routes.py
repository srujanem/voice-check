from flask import Blueprint, request, jsonify, Response
from io import BytesIO
from backend.config import Config
from backend.decorators import require_api_key

watermark_bp = Blueprint('watermark', __name__)

@watermark_bp.route("/verify_watermark", methods=["POST"])
@require_api_key
def verify_watermark():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    file = request.files["image"]
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    data = file.read()
    if b'VOICECHECK_AUTH_SIGNATURE' in data:
        return jsonify({"status": "verified", "authentic": True})
    else:
        return jsonify({"status": "not_verified", "authentic": False})

@watermark_bp.route("/create_watermark", methods=["POST"])
@require_api_key
def create_watermark():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    file = request.files["image"]
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        data = file.read()
        watermarked_data = data + b"VOICECHECK_AUTH_SIGNATURE"
        
        return Response(
            watermarked_data,
            mimetype=file.mimetype,
            headers={"Content-disposition": f"attachment; filename=protected_{file.filename}"}
        )
    except Exception as e:
        print(f"Error watermarking: {e}")
        return jsonify({"error": "Failed to process image"}), 500
