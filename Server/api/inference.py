"""
ML Inference Engine — Loads trained models and runs predictions
Handles both Audio (VoiceShield) and Image (PixelGuard) detectors
Falls back to mock predictions when models aren't trained yet
"""
import time
import os
import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️  PyTorch not installed — running in full demo mode")
    print("    Install: pip install torch --index-url https://download.pytorch.org/whl/cu128")

from api.config import settings

# Lazy imports for ML libraries
_audio_imports_done = False
_image_imports_done = False


def _get_device():
    if not TORCH_AVAILABLE:
        return "cpu"
    if torch.cuda.is_available():
        return torch.device(f"cuda:{settings.cuda_device}")
    return torch.device("cpu")


class VoiceShieldInference:
    """Audio AI vs Human detector using Wav2Vec2 fine-tuned model"""

    def __init__(self):
        self.device = _get_device()
        self.model = None
        self.processor = None
        self.model_version = "v0.0.0-untrained"
        if TORCH_AVAILABLE:
            self._load_model()
        else:
            print("ℹ️ VoiceShield: PyTorch not available — running in demo mode")

    def _load_model(self):
        """Load trained model if checkpoint exists"""
        checkpoint_path = Path(settings.audio_model_path)
        if checkpoint_path.exists():
            try:
                from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor
                print(f"🎙️ Loading VoiceShield from {checkpoint_path}...")
                checkpoint = torch.load(checkpoint_path, map_location=self.device)
                # Load model architecture
                self.model = Wav2Vec2ForSequenceClassification.from_pretrained(
                    "facebook/wav2vec2-base",
                    num_labels=2,
                    state_dict=checkpoint.get("model_state_dict", checkpoint)
                )
                self.model.to(self.device)
                self.model.eval()
                self.processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
                self.model_version = checkpoint.get("version", "v1.0.0")
                print(f"✅ VoiceShield loaded — version {self.model_version}")
            except Exception as e:
                print(f"⚠️ Could not load audio model: {e}. Using mock mode.")
                self.model = None
        else:
            print("ℹ️ Audio model not found — running in demo mode (train first!)")

    def predict(self, audio_path: str) -> Dict[str, Any]:
        """Run inference on an audio file"""
        start = time.time()

        if self.model is not None:
            return self._real_predict(audio_path, start)
        else:
            return self._mock_predict(audio_path, start)

    def _real_predict(self, audio_path: str, start: float) -> Dict[str, Any]:
        """Real model inference"""
        import torchaudio
        waveform, sample_rate = torchaudio.load(audio_path)
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)

        inputs = self.processor(
            waveform.squeeze().numpy(),
            sampling_rate=16000,
            return_tensors="pt",
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            if settings.mixed_precision and self.device.type == "cuda":
                with torch.autocast("cuda"):
                    logits = self.model(**inputs).logits
            else:
                logits = self.model(**inputs).logits

        probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
        ai_prob = float(probs[0])
        human_prob = float(probs[1])
        processing_ms = (time.time() - start) * 1000

        return {
            "ai_probability": round(ai_prob, 4),
            "human_probability": round(human_prob, 4),
            "confidence": round(max(ai_prob, human_prob), 4),
            "processing_time_ms": round(processing_ms, 2),
            "model_version": self.model_version,
            "device_used": str(self.device)
        }

    def _mock_predict(self, audio_path: str, start: float) -> Dict[str, Any]:
        """Mock prediction when model isn't trained yet"""
        filename = Path(audio_path).name.lower()
        # Simulate predictions based on filename hints
        if any(kw in filename for kw in ["ai", "synthetic", "tts", "generated"]):
            ai_prob, human_prob = 0.87, 0.13
        elif any(kw in filename for kw in ["human", "real", "person"]):
            ai_prob, human_prob = 0.11, 0.89
        else:
            ai_prob = np.random.uniform(0.3, 0.8)
            human_prob = 1.0 - ai_prob

        processing_ms = (time.time() - start) * 1000 + np.random.uniform(50, 200)
        return {
            "ai_probability": round(ai_prob, 4),
            "human_probability": round(human_prob, 4),
            "confidence": round(max(ai_prob, human_prob), 4),
            "processing_time_ms": round(processing_ms, 2),
            "model_version": "demo-v0.0",
            "device_used": "cpu (demo)"
        }


class PixelGuardInference:
    """Image AI vs Human detector using EfficientNet-B4 fine-tuned model"""

    def __init__(self):
        self.device = _get_device()
        self.model = None
        self.transform = None
        self.model_version = "v0.0.0-untrained"
        if TORCH_AVAILABLE:
            self._load_model()
        else:
            print("ℹ️ PixelGuard: PyTorch not available — running in demo mode")

    def _load_model(self):
        """Load trained model if checkpoint exists"""
        checkpoint_path = Path(settings.image_model_path)
        if checkpoint_path.exists():
            try:
                import timm
                from torchvision import transforms
                print(f"🖼️ Loading PixelGuard from {checkpoint_path}...")
                checkpoint = torch.load(checkpoint_path, map_location=self.device)

                self.model = timm.create_model("efficientnet_b4", pretrained=False, num_classes=2)
                self.model.load_state_dict(checkpoint.get("model_state_dict", checkpoint))
                self.model.to(self.device)
                self.model.eval()
                self.model_version = checkpoint.get("version", "v1.0.0")

                self.transform = transforms.Compose([
                    transforms.Resize((380, 380)),
                    transforms.CenterCrop(380),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
                print(f"✅ PixelGuard loaded — version {self.model_version}")
            except Exception as e:
                print(f"⚠️ Could not load image model: {e}. Using mock mode.")
                self.model = None
        else:
            print("ℹ️ Image model not found — running in demo mode (train first!)")

    def predict(self, image_path: str) -> Dict[str, Any]:
        """Run inference on an image file"""
        start = time.time()

        if self.model is not None:
            return self._real_predict(image_path, start)
        else:
            return self._mock_predict(image_path, start)

    def _real_predict(self, image_path: str, start: float) -> Dict[str, Any]:
        """Real model inference with FFT artifact analysis"""
        from PIL import Image
        import torch.fft

        img = Image.open(image_path).convert("RGB")
        tensor = self.transform(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            if settings.mixed_precision and self.device.type == "cuda":
                with torch.autocast("cuda"):
                    logits = self.model(tensor)
            else:
                logits = self.model(tensor)

        probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
        ai_prob = float(probs[0])
        human_prob = float(probs[1])

        # FFT analysis for GAN fingerprints
        gray_tensor = tensor.squeeze().mean(dim=0)
        fft = torch.fft.fft2(gray_tensor)
        fft_magnitude = torch.abs(fft).cpu().numpy()
        fft_peak_ratio = float(fft_magnitude.max() / (fft_magnitude.mean() + 1e-8))

        processing_ms = (time.time() - start) * 1000
        return {
            "ai_probability": round(ai_prob, 4),
            "human_probability": round(human_prob, 4),
            "confidence": round(max(ai_prob, human_prob), 4),
            "processing_time_ms": round(processing_ms, 2),
            "model_version": self.model_version,
            "fft_peak_ratio": round(fft_peak_ratio, 4),
            "device_used": str(self.device)
        }

    def _mock_predict(self, image_path: str, start: float) -> Dict[str, Any]:
        """Mock prediction when model isn't trained yet"""
        filename = Path(image_path).name.lower()
        if any(kw in filename for kw in ["ai", "synthetic", "generated", "midjourney", "dalle", "sd"]):
            ai_prob, human_prob = 0.91, 0.09
        elif any(kw in filename for kw in ["real", "human", "photo", "selfie"]):
            ai_prob, human_prob = 0.08, 0.92
        else:
            ai_prob = np.random.uniform(0.3, 0.8)
            human_prob = 1.0 - ai_prob

        processing_ms = (time.time() - start) * 1000 + np.random.uniform(30, 150)
        return {
            "ai_probability": round(ai_prob, 4),
            "human_probability": round(human_prob, 4),
            "confidence": round(max(ai_prob, human_prob), 4),
            "processing_time_ms": round(processing_ms, 2),
            "model_version": "demo-v0.0",
            "fft_peak_ratio": round(np.random.uniform(10, 50), 4),
            "device_used": "cpu (demo)"
        }


def get_prediction_label(ai_prob: float, threshold: float = 0.65) -> Tuple[str, str, str]:
    """
    Returns: (prediction_enum, label_text, label_color)
    """
    if ai_prob >= threshold:
        return "ai_generated", "🤖 AI Generated", "#FF4757"
    elif (1 - ai_prob) >= threshold:
        return "human", "👤 Human", "#2ED573"
    else:
        return "uncertain", "❓ Uncertain", "#FFA502"


# ===== Singleton instances =====
_voice_shield: Optional[VoiceShieldInference] = None
_pixel_guard: Optional[PixelGuardInference] = None


def get_voice_shield() -> VoiceShieldInference:
    global _voice_shield
    if _voice_shield is None:
        _voice_shield = VoiceShieldInference()
    return _voice_shield


def get_pixel_guard() -> PixelGuardInference:
    global _pixel_guard
    if _pixel_guard is None:
        _pixel_guard = PixelGuardInference()
    return _pixel_guard
