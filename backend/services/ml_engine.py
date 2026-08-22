import os
import tensorflow as tf
from backend.config import Config

class MLEngine:
    def __init__(self):
        self.voice_model = None
        self.voice_scaler = None
        self.image_model = None
        self.vit_model = None
        self.text_model = None
        self.text_vectorizer = None

        self._voice_attempted = False
        self._image_attempted = False
        self.reload_text_model()

    def get_voice_model(self):
        if not self._voice_attempted:
            self._voice_attempted = True
            try:
                import joblib, tensorflow as tf
                base_dir = Config.BASE_DIR
                self.voice_model = tf.keras.models.load_model(os.path.join(base_dir, "model.keras"))
                self.voice_scaler = joblib.load(os.path.join(base_dir, "scaler.pkl"))
            except: pass
        return self.voice_model, self.voice_scaler

    def get_image_model(self):
        if not self._image_attempted:
            self._image_attempted = True
            try:
                import tensorflow as tf
                base_dir = Config.BASE_DIR
                self.image_model = tf.keras.models.load_model(os.path.join(base_dir, "model_image_advanced.keras"))
                
                # Also load ViT
                import torch
                import torch.nn as nn
                from transformers import ViTModel
                class DeepfakeViT(nn.Module):
                    def __init__(self):
                        super().__init__()
                        self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
                        self.classifier = nn.Sequential(nn.Linear(self.vit.config.hidden_size, 256), nn.ReLU(), nn.Dropout(0.3), nn.Linear(256, 1))
                    def forward(self, pixel_values):
                        return self.classifier(self.vit(pixel_values=pixel_values).pooler_output)
                
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                self.vit_model = DeepfakeViT().to(device)
                vit_path = os.path.join(base_dir, "model_image_vit_best.pth")
                if os.path.exists(vit_path):
                    self.vit_model.load_state_dict(torch.load(vit_path, map_location=device))
                    self.vit_model.eval()
                else:
                    self.vit_model = None
            except Exception as e:
                print(f"Error loading image models: {e}")
        return self.image_model, self.vit_model

    def reload_text_model(self):
        import joblib
        base_dir = Config.BASE_DIR
        try:
            self.text_model = joblib.load(os.path.join(base_dir, "text_model.pkl"))
            self.text_vectorizer = joblib.load(os.path.join(base_dir, "text_vectorizer.pkl"))
        except: pass

ml = MLEngine()
