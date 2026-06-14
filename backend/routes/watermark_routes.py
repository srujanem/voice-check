from flask import Blueprint, request, jsonify, Response

watermark_bp = Blueprint('watermark', __name__)

@watermark_bp.route("/watermark", methods=["POST"])
def watermark():
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
