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
        
        self.text_transformer_model = None
        self.text_transformer_tokenizer = None
        self.text_transformer_device = None

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
                
                # Also load Advanced Model (ConvNeXt-V2 via timm)
                import torch
                import timm
                
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                
                try:
                    self.vit_model = timm.create_model('convnextv2_tiny.fcmae_ft_in22k_in1k', pretrained=False, num_classes=2)
                    self.vit_model = self.vit_model.to(device)
                    convnext_path = os.path.join(base_dir, "model_image_convnext_best.pth")
                    
                    if os.path.exists(convnext_path):
                        self.vit_model.load_state_dict(torch.load(convnext_path, map_location=device))
                        self.vit_model.eval()
                    else:
                        self.vit_model = None
                except Exception as e:
                    print(f"Error loading ConvNeXt model: {e}")
                    self.vit_model = None
            except Exception as e:
                print(f"Error loading image models: {e}")
        return self.image_model, self.vit_model

    def reload_text_model(self):
        import joblib
        import os
        base_dir = Config.BASE_DIR
        
        # Load transformer model if it exists
        transformer_path = os.path.join(base_dir, "model_text_finetuned")
        if os.path.exists(transformer_path):
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                import torch
                self.text_transformer_tokenizer = AutoTokenizer.from_pretrained(transformer_path)
                self.text_transformer_model = AutoModelForSequenceClassification.from_pretrained(transformer_path)
                self.text_transformer_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                self.text_transformer_model.to(self.text_transformer_device)
                self.text_transformer_model.eval()
                print("PyTorch Fine-Tuned Transformer text model loaded successfully!")
            except Exception as e:
                print(f"Error loading transformer text model: {e}")
                self.text_transformer_model = None
        else:
            self.text_transformer_model = None

        # Fallback to TF-IDF
        try:
            self.text_model = joblib.load(os.path.join(base_dir, "text_model.pkl"))
            self.text_vectorizer = joblib.load(os.path.join(base_dir, "text_vectorizer.pkl"))
            if not self.text_transformer_model:
                print("Sklearn TF-IDF text model loaded successfully!")
        except: pass

ml = MLEngine()
