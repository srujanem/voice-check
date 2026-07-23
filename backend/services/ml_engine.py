import os
import pickle
import tensorflow as tf
import stylometric_transformer
import xgboost   # Required for VotingClassifier deserialization (XGBClassifier)
import lightgbm  # Required for VotingClassifier deserialization (LGBMClassifier)
from backend.config import Config

class MLEngine:
    def __init__(self):
        self.voice_model = None
        self.voice_scaler = None
        self.image_model = None
        self.text_model = None
        self.text_vectorizer = None
        self.load_models()

    def load_models(self):
        base_dir = Config.BASE_DIR
        
        # Load Voice Model
        try:
            import joblib
            self.voice_model = tf.keras.models.load_model(os.path.join(base_dir, "model.keras"))
            self.voice_scaler = joblib.load(os.path.join(base_dir, "scaler.pkl"))
            print("Voice model and scaler loaded.")
        except Exception as e:
            print(f"Could not load voice model: {e}")

        # Load Image Model
        try:
            self.image_model = tf.keras.models.load_model(os.path.join(base_dir, "model_image.keras"))
            print("Image model loaded.")
        except Exception as e:
            print(f"Could not load image model: {e}")

        # Load Text Model (always reads from disk, never from Python module cache)
        self.reload_text_model()

    def reload_text_model(self):
        """Hot-reload the text model from disk. Call this after retraining."""
        import joblib
        base_dir = Config.BASE_DIR
        text_model_path = os.path.join(base_dir, "text_model.pkl")
        text_vec_path   = os.path.join(base_dir, "text_vectorizer.pkl")
        try:
            if not os.path.exists(text_model_path) or not os.path.exists(text_vec_path):
                print("Text model files not found – run train_text.py first.")
                return
            self.text_model      = joblib.load(text_model_path)
            self.text_vectorizer = joblib.load(text_vec_path)
            n_classes = getattr(self.text_model, 'classes_', [None, None])
            print(f"Text model loaded: {type(self.text_model).__name__} | classes={list(n_classes)}")
        except Exception as e:
            print(f"Could not load text model: {e}")
            self.text_model      = None
            self.text_vectorizer = None

ml = MLEngine()
