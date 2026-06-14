from flask import Blueprint, request, jsonify
import tensorflow as tf
from PIL import Image
from backend.services.ml_engine import ml
from backend.decorators import require_api_key

image_bp = Blueprint('image', __name__)

@image_bp.route("/predict_image", methods=["POST"])
@require_api_key
def predict_image():
    if ml.image_model is None:
        return jsonify({"error": "Image model not loaded."}), 500

    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]
    if file.filename == '':
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

        img = Image.open(file).convert('RGB')
        img = img.resize((224, 224))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)

        pred_prob = float(ml.image_model.predict(img_array, verbose=0)[0][0])
        is_fake = pred_prob >= 0.5

        result = "AI-Generated" if is_fake else "Authentic"
        prob_fake = round(pred_prob * 100, 1)
        prob_real = round((1.0 - pred_prob) * 100, 1)
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
