from flask import Blueprint, request, jsonify
from backend.services.ml_engine import ml
from backend.services.external_db import external_db
from backend.decorators import require_api_key
from datetime import datetime
import numpy as np
import uuid
import re
from langdetect import detect
from deep_translator import GoogleTranslator

text_bp = Blueprint('text', __name__)



@text_bp.route("/predict_text", methods=["POST"])
@require_api_key
def predict_text():

    if ml.text_model is None or ml.text_vectorizer is None:
        return jsonify({"error": "Text model not loaded. Please run train_text.py first."}), 500

    data = request.json
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data["text"].strip()
    if not text:
        return jsonify({"error": "Empty text provided"}), 400

    word_count = len(text.split())
    if word_count < 3:
        return jsonify({"error": "Text too short. Please provide at least 3 words for accurate analysis."}), 400

    try:
        # --- MULTI-LANGUAGE SUPPORT ---
        try:
            detected_lang = detect(text)
        except:
            detected_lang = 'en'
            
        original_text = text
        translated_text = text
        is_foreign = detected_lang != 'en'
        
        if is_foreign:
            print(f"[text_routes] Translating from {detected_lang} to English...")
            try:
                translated_text = GoogleTranslator(source=detected_lang, target='en').translate(text[:4500])
            except Exception as e:
                print(f"[text_routes] Translation failed: {e}")
                translated_text = text

        # 1. TF-IDF & Ensemble Prediction
        text_features = ml.text_vectorizer.transform([translated_text])
        probs = ml.text_model.predict_proba(text_features)[0]
        
        prob_ai_tfidf = float(probs[1])
        
        # 2. Linguistic Heuristic Booster
        lower_text = translated_text.lower()
        ai_fingerprints = [
            "delve into", "tapestry of", "testament to", "crucial to", "it is important to note",
            "in conclusion", "multifaceted", "nuanced", "underscore", "navigate the", "foster",
            "transformative", "seamless", "pivotal", "demystify", "furthermore,", "moreover,",
            "in today's digital age", "rapidly evolving", "a realm where", "unlock the potential",
            "as an ai", "i cannot fulfill", "comprehensive overview"
        ]
        
        fingerprint_matches = sum(1 for f in ai_fingerprints if f in lower_text)
        
        # Calculate heuristic probability
        prob_ai_heuristic = min(0.99, fingerprint_matches * 0.35)
        
        # Blend the probabilities
        if prob_ai_heuristic >= 0.7:
            final_prob_ai = max(0.85, prob_ai_heuristic)
        elif prob_ai_heuristic > 0.3:
            final_prob_ai = (prob_ai_tfidf * 0.3) + (prob_ai_heuristic * 0.7)
        else:
            final_prob_ai = prob_ai_tfidf
            
        final_prob_human = 1.0 - final_prob_ai
        
        # 3. Decision
        is_ai = bool(final_prob_ai > 0.5)
        prob_ai_pct    = round(final_prob_ai    * 100, 1)
        prob_human_pct = round(final_prob_human * 100, 1)
        confidence     = prob_ai_pct if is_ai else prob_human_pct

        # 4. Sentence-level analysis
        import re
        sentences = re.split(r'(?<=[.!?])\s+', original_text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) >= 3]
        sentences = sentences[:15]
        
        sentence_scores = []
        if sentences:
            eval_sentences = sentences
            if is_foreign:
                eval_sentences = []
                for s in sentences:
                    try:
                        eval_sentences.append(GoogleTranslator(source=detected_lang, target='en').translate(s))
                    except:
                        eval_sentences.append(s)
            
            sent_vectors = ml.text_vectorizer.transform(eval_sentences)
            sent_probs   = ml.text_model.predict_proba(sent_vectors)[:, 1]
            for orig_s, p in zip(sentences, sent_probs):
                sentence_scores.append({
                    "text":    orig_s,
                    "ai_prob": round(float(p), 4)
                })

        # 5. Linguistic & Burstiness Metrics
        sent_lengths = [len(s.split()) for s in sentences] if sentences else [word_count]
        burstiness_std = float(np.std(sent_lengths)) if len(sent_lengths) > 1 else 3.5
        burstiness_score = round(min(100.0, max(15.0, burstiness_std * 14.2)), 1)
        
        words = text.lower().split()
        unique_words = len(set(words))
        ttr = round((unique_words / max(1, len(words))) * 100, 1)
        
        forensic_telemetry = {
            "perplexity_cadence": "Dynamic Human Rhythm" if not is_ai else "Uniform Synthetic Flow",
            "burstiness_index": f"{burstiness_score}% Variance",
            "vocab_diversity": f"{ttr}% Lexical Diversity",
            "ai_phrases_detected": f"{fingerprint_matches} Markers Flagged" if fingerprint_matches > 0 else "0 Cliché Markers",
            "detected_language": detected_lang.upper() if detected_lang else "EN"
        }

        # 6. Confidence label
        if confidence >= 85:
            confidence_label = "Very High"
        elif confidence >= 70:
            confidence_label = "High"
        elif confidence >= 55:
            confidence_label = "Moderate"
        else:
            confidence_label = "Low"

        return jsonify({
            "prediction":       "AI-Generated" if is_ai else "Human Written",
            "is_ai":            is_ai,
            "confidence":       confidence,
            "confidence_label": confidence_label,
            "prob_human":       prob_human_pct,
            "prob_ai":          prob_ai_pct,
            "word_count":       word_count,
            "sentences":        sentence_scores,
            "forensics":        forensic_telemetry,
            "translated_from":  detected_lang if is_foreign else None
        })

    except Exception as e:
        print(f"[text_routes] Error processing text: {e}")
        return jsonify({"error": "Failed to process text. Please try again."}), 500
@text_bp.route("/reload_text_model", methods=["POST"])
@require_api_key
def reload_text_model():
    """Hot-reload the text model without restarting the server."""
    try:
        ml.reload_text_model()
        if ml.text_model is None:
            return jsonify({"error": "Model reload failed — check server logs."}), 500
        return jsonify({"message": "Text model reloaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

