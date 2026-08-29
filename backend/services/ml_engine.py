import os
import numpy as np
from backend.config import Config

class TFLiteWrapper:
    def __init__(self, model_path):
        self.interpreter = None
        try:
            from ai_edge_litert.interpreter import Interpreter
            self.interpreter = Interpreter(model_path=model_path)
        except Exception:
            try:
                import tflite_runtime.interpreter as tflite
                self.interpreter = tflite.Interpreter(model_path=model_path)
            except Exception:
                import tensorflow as tf
                self.interpreter = tf.lite.Interpreter(model_path=model_path)
            
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict(self, x, verbose=0):
        x = np.array(x, dtype=np.float32)
        self.interpreter.set_tensor(self.input_details[0]['index'], x)
        self.interpreter.invoke()
        return self.interpreter.get_tensor(self.output_details[0]['index'])


class ONNXWrapper:
    def __init__(self, model_path):
        import onnxruntime as ort
        self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, x, **kwargs):
        x = np.array(x, dtype=np.float32)
        return self.session.run(None, {self.input_name: x})[0]


class MLEngine:
    def __init__(self):
        self.voice_model = None
        self.voice_scaler = None
        self.image_model = None
        self.vit_model = None
        self.text_model = None
        self.text_vectorizer = None
        self.document_model = None

        self._voice_attempted = False
        self._image_attempted = False
        self._document_attempted = False
        self.reload_text_model()

    def get_voice_model(self):
        if not self._voice_attempted:
            self._voice_attempted = True
            base_dir = Config.BASE_DIR
            tflite_path = os.path.join(base_dir, "model_voice.tflite")
            keras_path = os.path.join(base_dir, "model.keras")
            
            try:
                import joblib
                self.voice_scaler = joblib.load(os.path.join(base_dir, "scaler.pkl"))
            except Exception as e:
                print(f"Voice scaler load error: {e}")

            if os.path.exists(tflite_path):
                try:
                    self.voice_model = TFLiteWrapper(tflite_path)
                    print("[ML Engine] Loaded ultra-fast Voice LiteRT model!")
                except Exception as e:
                    print(f"Failed to load Voice LiteRT: {e}")

            if self.voice_model is None and os.path.exists(keras_path):
                try:
                    import tensorflow as tf
                    self.voice_model = tf.keras.models.load_model(keras_path)
                    print("[ML Engine] Loaded Voice Keras model.")
                except Exception as e:
                    print(f"Voice Keras load error: {e}")

        return self.voice_model, self.voice_scaler

    def get_image_model(self):
        if not self._image_attempted:
            self._image_attempted = True
            base_dir = Config.BASE_DIR
            tflite_path = os.path.join(base_dir, "model_image.tflite")
            keras_path = os.path.join(base_dir, "model_image_advanced.keras")

            if os.path.exists(tflite_path):
                try:
                    self.image_model = TFLiteWrapper(tflite_path)
                    print("[ML Engine] Loaded ultra-fast Image LiteRT model!")
                except Exception as e:
                    print(f"Failed to load Image LiteRT: {e}")

            if self.image_model is None and os.path.exists(keras_path):
                try:
                    import tensorflow as tf
                    self.image_model = tf.keras.models.load_model(keras_path)
                    print("[ML Engine] Loaded Image Keras model.")
                except Exception as e:
                    print(f"Image Keras load error: {e}")

            self.vit_model = None

        return self.image_model, self.vit_model

    def reload_text_model(self):
        import joblib
        base_dir = Config.BASE_DIR
        try:
            self.text_model = joblib.load(os.path.join(base_dir, "text_model.pkl"))
            self.text_vectorizer = joblib.load(os.path.join(base_dir, "text_vectorizer.pkl"))
            print("[ML Engine] Sklearn TF-IDF text model loaded successfully!")
        except Exception as e:
            print(f"Text model load error: {e}")

    def analyze_document(self, img):
        base_dir = Config.BASE_DIR
        onnx_path = os.path.join(base_dir, "models", "model_document_forgery.onnx")
        pth_path = os.path.join(base_dir, "models", "model_document_forgery.pth")

        if os.path.exists(onnx_path):
            if self.document_model is None or not isinstance(self.document_model, ONNXWrapper):
                self.document_model = ONNXWrapper(onnx_path)
                print("[ML Engine] Using Document Forgery ONNX engine.")

            img_res = img.resize((224, 224))
            arr = np.array(img_res, dtype=np.float32) / 255.0
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            arr = (arr - mean) / std
            arr = np.transpose(arr, (2, 0, 1))
            arr = np.expand_dims(arr, 0)

            logits = self.document_model.predict(arr)[0]
            exp_logits = np.exp(logits - np.max(logits))
            probs = exp_logits / np.sum(exp_logits)
            prob_real = float(probs[0]) * 100
            prob_fake = float(probs[1]) * 100

            is_fake = prob_fake > 50.0
            confidence = prob_fake if is_fake else prob_real

            return {
                "prediction": "Forged/Tampered Document" if is_fake else "Authentic Document",
                "confidence": round(confidence, 1),
                "prob_human": round(prob_real, 1),
                "prob_ai": round(prob_fake, 1),
                "forensics": {
                    "ela_anomalies": is_fake,
                    "metadata_risk": "High" if is_fake else "Low"
                }
            }

        if os.path.exists(pth_path):
            import torch
            from torchvision import transforms, models
            import torch.nn as nn

            if self.document_model is None:
                device = torch.device("cpu")
                model = models.resnet18(weights=None)
                num_ftrs = model.fc.in_features
                model.fc = nn.Sequential(nn.Dropout(0.3), nn.Linear(num_ftrs, 2))
                model.load_state_dict(torch.load(pth_path, map_location=device, weights_only=True))
                model.eval()
                self.document_model = model

            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            input_tensor = transform(img).unsqueeze(0)
            with torch.no_grad():
                outputs = self.document_model(input_tensor)
                probs = torch.nn.functional.softmax(outputs, dim=1)[0]
                prob_real = float(probs[0]) * 100
                prob_fake = float(probs[1]) * 100

            is_fake = prob_fake > 50.0
            confidence = prob_fake if is_fake else prob_real

            return {
                "prediction": "Forged/Tampered Document" if is_fake else "Authentic Document",
                "confidence": round(confidence, 1),
                "prob_human": round(prob_real, 1),
                "prob_ai": round(prob_fake, 1),
                "forensics": {
                    "ela_anomalies": is_fake,
                    "metadata_risk": "High" if is_fake else "Low"
                }
            }

        raise Exception("No Document AI model found.")


ml = MLEngine()
