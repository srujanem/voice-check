import os
import subprocess
from flask import Blueprint, jsonify, request
from backend.decorators import require_api_key
from sync_dataset import sync_data

admin_bp = Blueprint('admin', __name__)

def verify_admin(req):
    user = getattr(req, 'user', None)
    if not user or user.get('email') != 'srujanem222@gmail.com':
        return False
    return True

@admin_bp.route('/api/admin/sync-data', methods=['POST'])
@require_api_key
def api_sync_data():
    if not verify_admin(request):
        return jsonify({"error": "Unauthorized"}), 403
        
    success, logs = sync_data()
    if success:
        return jsonify({"message": "Sync completed successfully", "logs": logs}), 200
    else:
        return jsonify({"error": "Sync failed", "logs": logs}), 500

@admin_bp.route('/api/admin/train-model', methods=['POST'])
@require_api_key
def api_train_model():
    if not verify_admin(request):
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.json or {}
    model_type = data.get('type', 'voice')
    
    script_map = {
        'voice': 'train.py',
        'image': 'train_image.py',
        'text': 'train_text.py'
    }
    
    script_name = script_map.get(model_type)
    if not script_name:
        return jsonify({"error": "Invalid model type"}), 400
        
    try:
        # Run the training script as a subprocess
        # We capture the output and return it
        result = subprocess.run(
            ['python', script_name],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Point to root
        )
        
        logs = result.stdout + "\n" + result.stderr
        
        if result.returncode == 0:
            return jsonify({"message": f"{model_type} model trained successfully", "logs": logs}), 200
        else:
            return jsonify({"error": f"Training failed with code {result.returncode}", "logs": logs}), 500
            
    except Exception as e:
        return jsonify({"error": f"Failed to execute training script: {str(e)}"}), 500
