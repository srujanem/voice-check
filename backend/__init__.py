from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from backend.config import Config
from backend.firebase_init import init_firebase
import os

def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(__name__, static_folder=base_dir, static_url_path='/')
    CORS(app)
    app.config.from_object(Config)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Initialize Firebase Admin SDK
    init_firebase()

    # Register Blueprints
    from backend.routes.voice_routes import voice_bp
    from backend.routes.image_routes import image_bp
    from backend.routes.text_routes import text_bp
    from backend.routes.video_routes import video_bp
    from backend.routes.url_routes import url_bp
    from backend.routes.watermark_routes import watermark_bp
    from backend.routes.history_routes import history_bp

    app.register_blueprint(voice_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(text_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(url_bp)
    app.register_blueprint(watermark_bp)
    app.register_blueprint(history_bp)

    @app.route("/", methods=["GET"])
    def home():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route("/api/status", methods=["GET"])
    def status():
        return jsonify({"status": "Voice Check API is running modularly with Firebase! ✅"})

    return app
