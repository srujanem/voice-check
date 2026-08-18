from flask import Blueprint, request, jsonify, current_app
import os
import shutil
import subprocess
from PIL import Image
import tensorflow as tf
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
        # Update status to PROCESSING
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

            image_model = ml.get_image_model()
            for frame_file in frames:
                frame_path = os.path.join(frames_dir, frame_file)
                img = Image.open(frame_path).convert('RGB')
                img = img.resize((224, 224))
                img_array = tf.keras.preprocessing.image.img_to_array(img)
                img_array = tf.expand_dims(img_array, 0)
                
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

            result_dict = {
                "prediction": result,
                "confidence": confidence,
                "prob_human": prob_real,
                "prob_ai": prob_fake
            }

            external_db.update_document('video_tasks', task_id, {
                "result_data": json.dumps(result_dict),
                "status": "COMPLETED"
            })
            
        except Exception as e:
            print(f"Error processing video task {task_id}: {e}")
            external_db.update_document('video_tasks', task_id, {
                "status": "FAILED",
                "error_msg": str(e)
            })
        finally:
            if os.path.exists(path):
                os.remove(path)


@video_bp.route("/predict_video", methods=["POST"])
@require_api_key
def predict_video():
    # Trigger lazy load and check if model is available
    _image_model = ml.get_image_model()
    if _image_model is None:
        return jsonify({"error": "Image model not loaded. Cannot process video frames."}), 500

    if "video" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["video"]
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    task_id = str(uuid.uuid4())
    # Save the file temporarily
    path = os.path.join(Config.UPLOAD_FOLDER, f"{task_id}_{file.filename}")
    file.save(path)

    # Insert into External DB
    external_db.create_document('video_tasks', {"id": task_id, "status": "PENDING"})

    # Start background thread
    app = current_app._get_current_object()
    thread = threading.Thread(target=process_video_task, args=(app, task_id, path))
    thread.daemon = True
    thread.start()

    return jsonify({"task_id": task_id, "status": "PENDING"}), 202


@video_bp.route("/video_status/<task_id>", methods=["GET"])
@require_api_key
def video_status(task_id):
    resp = external_db.list_documents('video_tasks')
    if not resp.get("success"):
        return jsonify({"error": "Could not fetch task status"}), 500
        
    tasks = resp.get("data", [])
    task_data = next((t for t in tasks if t.get("id") == task_id or t.get("_id") == task_id), None)
    
    if not task_data:
        return jsonify({"error": "Task not found"}), 404
        
    status = task_data.get("status")
    
    if status == 'COMPLETED':
        return jsonify(json.loads(task_data.get("result_data", "{}")))
    elif status == 'FAILED':
        return jsonify({"error": task_data.get("error_msg", "Task failed")}), 500
    else:
        return jsonify({"status": status})
