import os
import pickle
import tensorflow as tf
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

        # Load Text Model
        try:
            import joblib
            self.text_model = joblib.load(os.path.join(base_dir, "text_model.pkl"))
            self.text_vectorizer = joblib.load(os.path.join(base_dir, "text_vectorizer.pkl"))
            print("Text model loaded.")
        except Exception as e:
            print(f"Could not load text model: {e}")

ml = MLEngine()
