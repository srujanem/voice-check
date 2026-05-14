from flask import Flask, request, jsonify
from flask_cors import CORS
import static_ffmpeg
static_ffmpeg.add_paths()
import librosa
import numpy as np
import joblib
import os

app = Flask(__name__)
CORS(app)

model = joblib.load("model.pkl")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'webm', 'mp4', 'ogg', 'm4a'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_features(file_path):
    try:
        y, sr = librosa.load(file_path, duration=5, sr=22050)
        if len(y) == 0:
            return None
        # Pad audio if it's too short for mfcc calculation (n_fft=2048)
        if len(y) < 2048:
            y = np.pad(y, (0, 2048 - len(y)))
            
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        mel = librosa.feature.melspectrogram(y=y, sr=sr)
        features = np.hstack([
            np.mean(mfcc.T, axis=0),
            np.mean(chroma.T, axis=0),
            np.mean(mel.T, axis=0)
        ])
        return features.reshape(1, -1)
    except Exception as e:
        print(f"Error extracting features: {e}")
        return None

@app.route("/predict", methods=["POST"])
def predict():

    if "audio" not in request.files:
        return jsonify({"error": "No file uploaded"})

    file = request.files["audio"]

    if file.filename == '':
        return jsonify({"error": "No file selected"})
        
    if not allowed_file(file.filename):
        return jsonify({"error": f"Unsupported file format. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"})

    path = os.path.join(UPLOAD_FOLDER, file.filename)

    file.save(path)

    features = extract_features(path)

    if features is None:
        return jsonify({"error": "Failed to extract features from audio"})

    prediction = model.predict(features)[0]

    result = "Human Voice" if prediction == 0 else "AI Voice"

    return jsonify({
        "prediction": result
    })

if __name__ == "__main__":
    app.run(debug=True)
# model reloaded again