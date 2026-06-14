from flask import Blueprint, request, jsonify
import os
import librosa
import numpy as np
from backend.services.ml_engine import ml
from backend.config import Config

voice_bp = Blueprint('voice', __name__)

def extract_features(file_path):
    try:
        y, sr = librosa.load(file_path, sr=22050)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        return np.mean(mfccs.T, axis=0)
    except Exception as e:
        print(f"Error processing audio: {e}")
        return None

@voice_bp.route("/predict_voice", methods=["POST"])
def predict_voice():
    if ml.voice_model is None:
        return jsonify({"error": "Voice model not loaded on server."}), 500

    if "audio" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["audio"]
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    file_path = os.path.join(Config.UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    features = extract_features(file_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    if features is None:
        return jsonify({"error": "Could not extract features from audio. Try a different file."}), 422

    if ml.voice_scaler is not None:
        features = ml.voice_scaler.transform([features])

    pred_prob = float(ml.voice_model.predict(features, verbose=0)[0][0])
    is_ai = pred_prob >= 0.5

    result = "AI Voice" if is_ai else "Human Voice"
    prob_ai    = round(pred_prob * 100, 1)
    prob_human = round((1.0 - pred_prob) * 100, 1)
    confidence = prob_ai if is_ai else prob_human

    return jsonify({
        "prediction": result,
        "confidence": confidence,
        "prob_human": prob_human,
        "prob_ai":    prob_ai
    })
