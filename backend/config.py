import os

class Config:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
    
    SECRET_KEY = os.environ.get("SECRET_KEY", "voicecheck-super-secret-key")
