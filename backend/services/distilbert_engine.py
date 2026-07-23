"""
DistilBERT Inference Engine
Loads the fine-tuned DistilBERT model and runs fast inference for AI detection.
Used as a third signal alongside XGBoost Ensemble and Perplexity Engine.
"""

import os
import torch
import numpy as np

class DistilBERTEngine:
    def __init__(self):
        self.model     = None
        self.tokenizer = None
        self.device    = "cpu"   # Force CPU for stability on Windows
        self._load()

    def _load(self):
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "models", "deberta_ai_detector", "best_model"
        )
        if not os.path.exists(model_path):
            print("[DistilBERTEngine] Model not found — skipping. Run train_deberta.py first.")
            return
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model     = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.model.eval()
            self.model.to(self.device)
            print("[DistilBERTEngine] DistilBERT model loaded (98% accuracy).")
        except Exception as e:
            print(f"[DistilBERTEngine] Load failed (non-fatal): {e}")
            self.model     = None
            self.tokenizer = None

    def predict(self, text: str) -> dict:
        """
        Returns AI probability score from DistilBERT.
        Returns None if model not loaded.
        """
        if self.model is None or self.tokenizer is None:
            return None

        try:
            # Truncate to first 300 words for fast inference
            words = text.split()
            text_trunc = ' '.join(words[:300])

            inputs = self.tokenizer(
                text_trunc,
                return_tensors  = "pt",
                truncation      = True,
                max_length      = 128,
                padding         = True,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                logits = self.model(**inputs).logits
                probs  = torch.softmax(logits, dim=-1)[0].cpu().numpy()

            return {
                "prob_human": float(probs[0]),
                "prob_ai":    float(probs[1]),
            }
        except Exception as e:
            print(f"[DistilBERTEngine] Inference error (non-fatal): {e}")
            return None


# Singleton instance
distilbert_engine = DistilBERTEngine()
