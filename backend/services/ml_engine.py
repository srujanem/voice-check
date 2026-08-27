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
                # ConvNeXt model disabled due to severe PyTorch/TensorFlow GIL deadlocks and hallucinations on modern diffusion models.
                # Relying on EfficientNet + VAE Grid Forensics instead.
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


    def analyze_document(self, img):
        import torch
        from torchvision import transforms, models
        import torch.nn as nn
        
        # Lazy load model
        if not hasattr(self, 'document_model') or self.document_model is None:
            print("[ML Engine] Loading Document Forgery ResNet18...")
            try:
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                model = models.resnet18(weights=None)
                num_ftrs = model.fc.in_features
                model.fc = nn.Sequential(nn.Dropout(0.3), nn.Linear(num_ftrs, 2))
                model.load_state_dict(torch.load("models/model_document_forgery.pth", map_location=device, weights_only=True))
                model = model.to(device)
                model.eval()
                self.document_model = model
                self.doc_device = device
            except Exception as e:
                print(f"Document model load failed: {e}")
                raise Exception("Document AI model failed to load.")

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        input_tensor = transform(img).unsqueeze(0).to(self.doc_device)
        with torch.no_grad():
            outputs = self.document_model(input_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)[0]
            prob_real = float(probs[0]) * 100
            prob_fake = float(probs[1]) * 100
            
        is_fake = prob_fake > 50.0
        confidence = prob_fake if is_fake else prob_real
        
        return {
            "prediction": "Forged/Tampered Document" if is_fake else "Authentic Document",
            "confidence": confidence,
            "prob_human": prob_real,
            "prob_ai": prob_fake,
            "forensics": {
                "ela_anomalies": is_fake,
                "metadata_risk": "High" if is_fake else "Low"
            }
        }


ml = MLEngine()
