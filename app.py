from flask import Flask, request, jsonify
from flask_cors import CORS
import static_ffmpeg
static_ffmpeg.add_paths()
import librosa
import numpy as np
import joblib
import os
import tensorflow as tf
from PIL import Image

app = Flask(__name__)
CORS(app)

# ── Load model & scaler ───────────────────────────────────────────────────────
model = tf.keras.models.load_model("model.keras")
try:
    scaler = joblib.load("scaler.pkl")
    print("Model and scaler loaded.")
except FileNotFoundError:
    scaler = None
    print("scaler.pkl not found — predictions may be less accurate.")

# --- Load Image Model ---
try:
    model_image = tf.keras.models.load_model("model_image.keras")
    print("Image model loaded.")
except Exception as e:
    model_image = None
    print("model_image.keras not found. Run train_image.py first.")

# --- Load Text Model ---
try:
    text_vectorizer = joblib.load("text_vectorizer.pkl")
    text_model = joblib.load("text_model.pkl")
    print("Text model loaded.")
except Exception as e:
    text_model = None
    text_vectorizer = None
    print("text_model.pkl not found. Run train_text.py first.")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'webm', 'mp4', 'ogg', 'm4a'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ── Feature extraction (must match train_model.py exactly) ───────────────────
def extract_features(file_path):
    try:
        y, sr = librosa.load(file_path, duration=5, sr=22050)

        if len(y) == 0:
            return None

        if len(y) < 2048:
            y = np.pad(y, (0, 2048 - len(y)))

        # MFCC
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)

        # Chroma
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)

        # Pitch
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = pitches[magnitudes > np.median(magnitudes)]
        pitch_mean = np.mean(pitch_values) if len(pitch_values) > 0 else 0.0
        pitch_std  = np.std(pitch_values)  if len(pitch_values) > 0 else 0.0

        # Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(y)

        # RMS Energy
        rms = librosa.feature.rms(y=y)

        features = np.hstack([
            np.mean(mfcc.T, axis=0),
            np.std(mfcc.T, axis=0),
            np.mean(chroma.T, axis=0),
            np.std(chroma.T, axis=0),
            [pitch_mean, pitch_std],
            [np.mean(zcr), np.std(zcr)],
            [np.mean(rms), np.std(rms)],
        ])
        return features.reshape(1, -1)

    except Exception as e:
        print(f"Feature extraction error: {e}")
        return None

# ── Predict endpoint ──────────────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():
    if "audio" not in request.files:
        return jsonify({"error": "No file uploaded"})

    file = request.files["audio"]

    if file.filename == '':
        return jsonify({"error": "No file selected"})

    if not allowed_file(file.filename):
        return jsonify({"error": f"Unsupported format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    features = extract_features(path)

    if features is None:
        return jsonify({"error": "Could not extract features from audio. Try a different file."}), 422

    if scaler is not None:
        features = scaler.transform(features)

    pred_prob = float(model.predict(features, verbose=0)[0][0])
    is_ai = pred_prob >= 0.5

    result = "AI Voice" if is_ai else "Human Voice"

    # Extra detail: individual class probabilities
    prob_ai    = round(pred_prob * 100, 1)
    prob_human = round((1.0 - pred_prob) * 100, 1)
    confidence = prob_ai if is_ai else prob_human

    print(f"Prediction: {result} | Confidence: {confidence}% | Human: {prob_human}% | AI: {prob_ai}%")

    return jsonify({
        "prediction": result,
        "confidence": confidence,
        "prob_human": prob_human,
        "prob_ai":    prob_ai
    })

# ── Predict Image endpoint ────────────────────────────────────────────────────
@app.route("/predict_image", methods=["POST"])
def predict_image():
    if model_image is None:
        return jsonify({"error": "Image model not loaded. Please run train_image.py first."}), 500

    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        img = Image.open(file.stream).convert('RGB')
        img = img.resize((224, 224))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0) # Create a batch

        pred_prob = float(model_image.predict(img_array, verbose=0)[0][0])
        is_fake = pred_prob >= 0.5 # Using sigmoid, assuming Fake is 1 and Real is 0.

        result = "AI-Generated" if is_fake else "Authentic"
        
        prob_fake = round(pred_prob * 100, 1)
        prob_real = round((1.0 - pred_prob) * 100, 1)
        confidence = prob_fake if is_fake else prob_real

        print(f"Image Prediction: {result} | Confidence: {confidence}% | Fake: {prob_fake}%")

        return jsonify({
            "prediction": result,
            "confidence": confidence,
            "prob_real": prob_real,
            "prob_fake": prob_fake
        })
    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({"error": "Failed to process image"}), 500

# ── Predict Text endpoint ─────────────────────────────────────────────────────
@app.route("/predict_text", methods=["POST"])
def predict_text():
    if text_model is None or text_vectorizer is None:
        return jsonify({"error": "Text model not loaded. Please run train_text.py first."}), 500

    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
        
    text = data['text'].strip()
    if not text:
        return jsonify({"error": "Empty text provided"}), 400

    try:
        features = text_vectorizer.transform([text])
        pred_prob = float(text_model.predict_proba(features)[0][1]) # Probability of class 1 (AI)
        is_ai = pred_prob >= 0.5
        
        result = "AI-Generated" if is_ai else "Human Written"
        
        prob_ai = round(pred_prob * 100, 1)
        prob_human = round((1.0 - pred_prob) * 100, 1)
        confidence = prob_ai if is_ai else prob_human

        print(f"Text Prediction: {result} | Confidence: {confidence}% | AI: {prob_ai}%")

        return jsonify({
            "prediction": result,
            "confidence": confidence,
            "prob_human": prob_human,
            "prob_ai": prob_ai
        })
    except Exception as e:
        print(f"Error processing text: {e}")
        return jsonify({"error": "Failed to process text"}), 500

# ── Health check ──────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Voice Check API is running ✅"})

if __name__ == "__main__":
    app.run(debug=True)
