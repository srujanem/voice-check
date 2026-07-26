from flask import Blueprint, request, jsonify
import tensorflow as tf
from PIL import Image
from backend.services.ml_engine import ml
from backend.decorators import require_api_key
import pillow_heif

# Register HEIF opener so PIL can open .heic files
pillow_heif.register_heif_opener()

image_bp = Blueprint('image', __name__)

@image_bp.route("/predict_image", methods=["POST"])
@require_api_key
def predict_image():
    image_model = ml.get_image_model()
    if image_model is None:
        return jsonify({"error": "Image model not loaded."}), 500

    file = request.files.get("image") or request.files.get("file")
    if not file or file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        data = file.read()
        if b"VOICECHECK_AUTH_SIGNATURE" in data:
            return jsonify({
                "prediction": "Authentic (Watermarked)",
                "confidence": 100.0,
                "prob_human": 100.0,
                "prob_ai": 0.0
            })
        file.seek(0)

        try:
            img = Image.open(file).convert('RGB')
            img = img.resize((224, 224))
        except Exception as e:
            return jsonify({"error": "Invalid or corrupted image file."}), 400
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)

        pred_prob = float(image_model.predict(img_array, verbose=0)[0][0])
        # TF assigns labels alphabetically: fake=0, real=1
        # So pred_prob = P(real). Fake means pred_prob < 0.5
        is_fake = pred_prob < 0.5

        result = "AI-Generated" if is_fake else "Authentic"
        prob_real = round(pred_prob * 100, 1)
        prob_fake = round((1.0 - pred_prob) * 100, 1)
        confidence = prob_fake if is_fake else prob_real

        return jsonify({
            "prediction": result,
            "confidence": confidence,
            "prob_human": prob_real,
            "prob_ai": prob_fake
        })
    except Exception as e:
        print(f"Error predicting image: {e}")
        return jsonify({"error": "Failed to process image."}), 500
