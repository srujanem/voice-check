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
            self.voice_model = tf.keras.models.load_model(os.path.join(base_dir, "voice_model.h5"))
            with open(os.path.join(base_dir, "scaler.pkl"), "rb") as f:
                self.voice_scaler = pickle.load(f)
            print("Voice model and scaler loaded.")
        except Exception as e:
            print(f"Could not load voice model: {e}")

        # Load Image Model
        try:
            self.image_model = tf.keras.models.load_model(os.path.join(base_dir, "image_model.h5"))
            print("Image model loaded.")
        except Exception as e:
            print(f"Could not load image model: {e}")

        # Load Text Model
        try:
            with open(os.path.join(base_dir, "text_model.pkl"), "rb") as f:
                self.text_model = pickle.load(f)
            with open(os.path.join(base_dir, "text_vectorizer.pkl"), "rb") as f:
                self.text_vectorizer = pickle.load(f)
            print("Text model loaded.")
        except Exception as e:
            print(f"Could not load text model: {e}")

ml = MLEngine()
