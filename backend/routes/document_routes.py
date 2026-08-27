from flask import Blueprint, request, jsonify
from backend.services.ml_engine import ml
from backend.decorators import require_api_key
import io
from PIL import Image

document_bp = Blueprint("document", __name__)

@document_bp.route('/predict_document', methods=['POST'])
@require_api_key
def predict_document():
    # Frontend sends form data with file named "image" (same as deepfake ui fallback) or "document"
    file = request.files.get('document') or request.files.get('image')
    if not file or file.filename == '':
        return jsonify({"error": "No document file uploaded."}), 400
        
    try:
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        
        result = ml.analyze_document(img)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
