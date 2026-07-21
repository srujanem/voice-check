from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from backend.config import Config
import os

def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(__name__, static_folder=base_dir, static_url_path='/')
    CORS(app)
    app.config.from_object(Config)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    # Register Blueprints
    from backend.routes.voice_routes import voice_bp
    from backend.routes.image_routes import image_bp
    from backend.routes.text_routes import text_bp
    from backend.routes.video_routes import video_bp
    from backend.routes.url_routes import url_bp
    from backend.routes.watermark_routes import watermark_bp
    from backend.routes.history_routes import history_bp
    from backend.routes.external_db_routes import external_db_bp
    from backend.routes.admin_routes import admin_bp
    from backend.routes.auth_routes import auth_bp

    app.register_blueprint(voice_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(text_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(url_bp)
    app.register_blueprint(watermark_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(external_db_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)

    @app.route("/", methods=["GET"])
    def home():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route("/api/status", methods=["GET"])
    def status():
        return jsonify({"status": "Voice Check API is running modularly with Firebase! ✅"})

    @app.route("/api/health", methods=["GET"])
    def api_health():
        return jsonify({"status": "ok", "version": "2.0"})

    @app.route("/api/infer", methods=["POST"])
    def api_infer():
        from flask import request
        import io
        
        req_type = request.form.get("type", "voice")
        file = request.files.get("file")
        
        if not file:
            return jsonify({"error": "No file uploaded"}), 400
            
        client = app.test_client()
        file_content = file.read()
        
        type_map = {
            "voice": ("/predict_voice", "audio"),
            "image": ("/predict_image", "image"),
            "video": ("/predict_video", "video")
        }
        
        if req_type == "text":
            # For batch-ui which uploads text files
            text_data = file_content.decode('utf-8', errors='ignore')
            response = client.post('/predict_text', json={"text": text_data}, headers={'Authorization': request.headers.get('Authorization', '')})
        elif req_type in type_map:
            internal_route, file_key = type_map[req_type]
            response = client.post(
                internal_route,
                data={file_key: (io.BytesIO(file_content), file.filename)},
                content_type='multipart/form-data',
                headers={'Authorization': request.headers.get('Authorization', '')}
            )
        else:
            return jsonify({"error": f"Unsupported type: {req_type}"}), 400
            
        data = response.get_json()
        if response.status_code != 200:
            return jsonify(data) if data else jsonify({"error": "Internal error"}), response.status_code
            
        is_ai = False
        pred_str = str(data.get("prediction", "")).lower()
        if "ai" in pred_str or "fake" in pred_str or "generated" in pred_str:
            is_ai = True
            
        conf_val = float(data.get("prob_ai", data.get("confidence", 0.0))) / 100.0
        
        return jsonify({
            "is_ai": is_ai,
            "confidence": conf_val,
            "generator": "Unknown",
            "analysis": data
        })

    return app
