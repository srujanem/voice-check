import torch
import numpy as np
import re
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

class PerplexityEngine:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.load_model()

    def load_model(self):
        try:
            model_id = "distilgpt2"
            self.tokenizer = GPT2TokenizerFast.from_pretrained(model_id)
            self.model = GPT2LMHeadModel.from_pretrained(model_id)
            self.model.eval()
            print("[PerplexityEngine] distilgpt2 loaded successfully.")
        except Exception as e:
            print(f"[PerplexityEngine] Failed to load distilgpt2: {e}")

    def analyze(self, text):
        if self.model is None or self.tokenizer is None:
            return {"perplexity": 50.0, "burstiness": 0.0, "perplexity_std": 0.0}

        words = text.split()
        if len(words) < 5:
            return {"perplexity": 50.0, "burstiness": 0.0, "perplexity_std": 0.0}

        # 1. Overall Perplexity
        try:
            inputs = self.tokenizer(text, return_tensors="pt")
            input_ids = inputs.input_ids
            with torch.no_grad():
                outputs = self.model(input_ids, labels=input_ids)
                neg_log_likelihood = outputs.loss
            overall_ppl = torch.exp(neg_log_likelihood).item()
        except Exception:
            overall_ppl = 50.0

        # 2. Sentence-level Perplexity Variance & Burstiness
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip() and len(s.split()) >= 3]
        sentence_lengths = [len(s.split()) for s in sentences]
        burstiness = float(np.std(sentence_lengths)) if len(sentence_lengths) > 1 else 0.0

        sent_ppls = []
        for sent in sentences[:10]:
            try:
                s_inputs = self.tokenizer(sent, return_tensors="pt")
                s_ids = s_inputs.input_ids
                if s_ids.shape[1] >= 3:
                    with torch.no_grad():
                        s_out = self.model(s_ids, labels=s_ids)
                    s_ppl = torch.exp(s_out.loss).item()
                    sent_ppls.append(s_ppl)
            except Exception:
                pass

        ppl_std = float(np.std(sent_ppls)) if len(sent_ppls) > 1 else 0.0

        return {
            "perplexity": round(overall_ppl, 2),
            "burstiness": round(burstiness, 2),
            "perplexity_std": round(ppl_std, 2)
        }

perplexity_engine = PerplexityEngine()
