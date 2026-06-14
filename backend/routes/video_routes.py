from flask import Blueprint, request, jsonify
import os
import subprocess
from PIL import Image
import tensorflow as tf
from backend.services.ml_engine import ml
from backend.config import Config

video_bp = Blueprint('video', __name__)

@video_bp.route("/predict_video", methods=["POST"])
def predict_video():
    if ml.image_model is None:
        return jsonify({"error": "Image model not loaded. Cannot process video frames."}), 500

    if "video" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["video"]
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    path = os.path.join(Config.UPLOAD_FOLDER, file.filename)
    file.save(path)

    try:
        frames_dir = os.path.join(Config.UPLOAD_FOLDER, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        for f in os.listdir(frames_dir):
            os.remove(os.path.join(frames_dir, f))

        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", path, "-vf", "fps=1", "-vframes", "5",
            os.path.join(frames_dir, "frame_%03d.png")
        ]
        subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        frames = os.listdir(frames_dir)
        if not frames:
            raise Exception("No frames extracted.")

        total_prob = 0.0
        frame_count = 0

        for frame_file in frames:
            frame_path = os.path.join(frames_dir, frame_file)
            img = Image.open(frame_path).convert('RGB')
            img = img.resize((224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)
            
            pred_prob = float(ml.image_model.predict(img_array, verbose=0)[0][0])
            total_prob += pred_prob
            frame_count += 1
            os.remove(frame_path)

        avg_prob = total_prob / frame_count
        is_fake = avg_prob >= 0.5
        result = "AI-Generated" if is_fake else "Authentic"
        
        prob_fake = round(avg_prob * 100, 1)
        prob_real = round((1.0 - avg_prob) * 100, 1)
        confidence = prob_fake if is_fake else prob_real

        os.remove(path)
        return jsonify({
            "prediction": result,
            "confidence": confidence,
            "prob_human": prob_real,
            "prob_ai": prob_fake
        })

    except Exception as e:
        print(f"Error processing video: {e}")
        if os.path.exists(path):
            os.remove(path)
        return jsonify({"error": "Failed to process video. FFMPEG might not be installed."}), 500
