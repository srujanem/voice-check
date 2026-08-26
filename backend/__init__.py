from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from backend.config import Config
from backend.security import apply_security_headers, log_request
import os
import PyPDF2

def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(__name__, static_folder=base_dir, static_url_path='/')
    # ── CORS: allow all origins for all routes ──
    CORS(app, resources={r"/*": {
        "origins": "*",
        "allow_headers": ["Content-Type", "Authorization", "ngrok-skip-browser-warning", "X-Requested-With", "Accept"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "max_age": 600
    }})
    app.config.from_object(Config)
    # Reduce max upload to 50 MB hard ceiling
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

    # ── Security hooks ──
    app.after_request(apply_security_headers)
    app.before_request(log_request)

    # ── Rate limiter ──
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

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
    from backend.routes.results_routes import results_bp
    from backend.routes.alias_routes import alias_bp
    from backend.routes.feedback_routes import feedback_bp
    from backend.routes.document_routes import document_bp
    from backend.routes.billing_routes import billing_bp

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
    app.register_blueprint(results_bp)
    app.register_blueprint(alias_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(billing_bp)

    @app.route("/", methods=["GET"])
    def home():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route("/api/status", methods=["GET"])
    def status():
        return jsonify({"status": "Voice Check API is running modularly with Firebase! ✅"})

    @app.route("/api/health", methods=["GET"])
    def api_health():
        return jsonify({"status": "ok", "secure": True})

    # ── Error handlers ──
    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"error": "File too large. Maximum upload size is 50 MB."}), 413

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"error": "Too many requests. Please slow down."}), 429

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request."}), 400

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error. Please try again."}), 500


    @app.route("/api/infer", methods=["POST"])
    @limiter.limit("10 per minute")
    def api_infer():
        from flask import request
        from backend.security import validate_file_upload, log_suspicious
        import io
        
        req_type = request.form.get("type", "voice")
        file = request.files.get("file")
        
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        # Comprehensive file validation (type, size, magic bytes)
        scan_type = req_type if req_type in ("image", "audio", "video", "text", "document") else "audio"
        if req_type == "voice":
            scan_type = "voice"
        is_valid, err_msg = validate_file_upload(file, scan_type)
        if not is_valid:
            log_suspicious(f"File validation failed: {err_msg} | file={file.filename}")
            return jsonify({"error": err_msg}), 400
            
        client = app.test_client()
        file_content = file.read()
        
        type_map = {
            "voice": ("/predict_voice", "audio"),
            "image": ("/predict_image", "image"),
            "video": ("/predict_video", "video"),
            "document": ("/predict_document", "document")
        }
        
        if req_type == "text":
            fn = file.filename.lower()
            if fn.endswith(".pdf"):
                reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                text_data = ""
                for i in range(len(reader.pages)):
                    extracted = reader.pages[i].extract_text()
                    if extracted:
                        text_data += extracted + "\n"
            else:
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
        if response.status_code not in (200, 202):
            return jsonify(data) if data else jsonify({"error": "Internal error"}), response.status_code
            
        is_ai = False
        pred_str = str(data.get("prediction", "")).lower()
        if "ai" in pred_str or "fake" in pred_str or "generated" in pred_str:
            is_ai = True
            
        raw_conf = data.get("confidence")
        if raw_conf is not None:
            conf_val = float(raw_conf) / 100.0 if float(raw_conf) > 1.0 else float(raw_conf)
        else:
            prob_val = data.get("prob_ai") if is_ai else data.get("prob_human")
            conf_val = (float(prob_val) / 100.0) if prob_val is not None else 0.5

        return jsonify({
            "is_ai": is_ai,
            "confidence": conf_val,
            "generator": "Unknown",
            "analysis": data
        })

    return app
