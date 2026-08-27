from flask import Blueprint, request, jsonify, current_app
import os
import shutil
import subprocess
from PIL import Image
import numpy as np
import threading
import uuid
import json
from backend.services.ml_engine import ml
from backend.config import Config
from backend.services.external_db import external_db
from backend.decorators import require_api_key

video_bp = Blueprint('video', __name__)

def process_video_task(app, task_id, path):
    with app.app_context():
        external_db.update_document('video_tasks', task_id, {"status": "PROCESSING"})
        
        try:
            frames_dir = os.path.join(Config.UPLOAD_FOLDER, f"frames_{task_id}")
            os.makedirs(frames_dir, exist_ok=True)
            
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", path, "-vf", "fps=1", "-vframes", "5",
                os.path.join(frames_dir, "frame_%03d.png")
            ]
            subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            frames = os.listdir(frames_dir)
            if not frames:
                raise Exception("No frames extracted. File might not be a valid video.")

            total_prob = 0.0
            frame_count = 0

            image_model, _ = ml.get_image_model()
            for frame_file in frames:
                frame_path = os.path.join(frames_dir, frame_file)
                img = Image.open(frame_path).convert('RGB')
                img = img.resize((224, 224))
                img_array = np.array(img, dtype=np.float32)
                img_array = np.expand_dims(img_array, 0)
                
                pred_prob = float(image_model.predict(img_array, verbose=0)[0][0])
                total_prob += pred_prob
                frame_count += 1
                os.remove(frame_path)
                
            shutil.rmtree(frames_dir, ignore_errors=True)

            avg_prob = total_prob / frame_count
            is_fake = avg_prob < 0.5
            result = "AI-Generated" if is_fake else "Authentic"
            
            prob_real = round(avg_prob * 100, 1)
            prob_fake = round((1.0 - avg_prob) * 100, 1)
            confidence = prob_fake if is_fake else prob_real

            external_db.update_document('video_tasks', task_id, {
                "status": "COMPLETED",
                "result": result,
                "confidence": confidence,
                "prob_real": prob_real,
                "prob_fake": prob_fake
            })

        except Exception as e:
            external_db.update_document('video_tasks', task_id, {
                "status": "FAILED",
                "error": str(e)
            })
        finally:
            if os.path.exists(path):
                os.remove(path)

@video_bp.route("/predict_video", methods=["POST"])
@require_api_key
def predict_video():
    file = request.files.get("video") or request.files.get("file")
    if not file or file.filename == '':
        return jsonify({"error": "No video file selected"}), 400

    task_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(Config.UPLOAD_FOLDER, f"{task_id}{file_ext}")
    file.save(file_path)

    external_db.set_document('video_tasks', task_id, {
        "status": "QUEUED",
        "created_at": None
    })

    app = current_app._get_current_object()
    threading.Thread(target=process_video_task, args=(app, task_id, file_path)).start()

    return jsonify({
        "status": "QUEUED",
        "task_id": task_id,
        "message": "Video processing started in background"
    })

@video_bp.route("/video_status/<task_id>", methods=["GET"])
@require_api_key
def video_status(task_id):
    task = external_db.get_document('video_tasks', task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)
