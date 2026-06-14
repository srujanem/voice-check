from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.database import db
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    db.init_app(app)

    # Register Blueprints
    from backend.routes.voice_routes import voice_bp
    from backend.routes.image_routes import image_bp
    from backend.routes.text_routes import text_bp
    from backend.routes.video_routes import video_bp
    from backend.routes.url_routes import url_bp
    from backend.routes.watermark_routes import watermark_bp
    from backend.routes.auth_routes import auth_bp
    from backend.routes.history_routes import history_bp

    app.register_blueprint(voice_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(text_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(url_bp)
    app.register_blueprint(watermark_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(history_bp)

    @app.route("/", methods=["GET"])
    def home():
        return jsonify({"status": "Voice Check API is running modularly ✅"})

    return app
