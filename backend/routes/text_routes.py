from flask import Blueprint, request, jsonify
from backend.services.ml_engine import ml
from backend.services.external_db import external_db
from backend.decorators import require_api_key
from datetime import datetime
import numpy as np
import uuid
import re

text_bp = Blueprint('text', __name__)

# Generalizing AI Structural Patterns & Formal Discourse Markers
AI_DISCOURSE_MARKERS = [
    r"\b(in today'?s (fast-paced|rapidly changing|digital|modern|interconnected) world)\b",
    r"\b(plays a (crucial|vital|pivotal|key|paramount|central) role)\b",
    r"\b(it is (worth|important|crucial|essential|imperative) to (note|highlight|understand|consider|remember))\b",
    r"\b(furthermore|moreover|consequently|additionally|in conclusion|in summary|ultimately)\b",
    r"\b(delve|intricate|tapestry|testament|fosters|underscores|multifaceted|paradigm|transformative)\b",
    r"\b(overall|as a result|on the other hand|it should be noted|broadly speaking)\b"
]


def calculate_generalization_signals(text):
    """
    Computes model-agnostic structural stylometric features that generalize across AI models:
    1. Sentence length variance (Burstiness)
    2. Formal Discourse Markers
    3. Punctuation & Capitalization Uniformity
    """
    words = text.split()
    if not words:
        return 0.5

    # 1. Formal Discourse Markers
    text_lower = text.lower()
    marker_matches = 0
    for pat in AI_DISCOURSE_MARKERS:
        if re.search(pat, text_lower):
            marker_matches += 1

    # 2. Sentence Length Variance (Burstiness)
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sent_lengths = [len(s.split()) for s in sentences if len(s.split()) > 0]

    stylo_ai_score = 0.5

    if marker_matches >= 3:
        stylo_ai_score += 0.40
    elif marker_matches == 2:
        stylo_ai_score += 0.28
    elif marker_matches == 1:
        stylo_ai_score += 0.15

    if len(sent_lengths) >= 3:
        std_len = float(np.std(sent_lengths))
        mean_len = float(np.mean(sent_lengths))
        # AI text has highly uniform sentence lengths (low std_len)
        if std_len < 3.5 and mean_len > 10:
            stylo_ai_score += 0.15
        elif std_len > 8.0:
            stylo_ai_score -= 0.15

    return min(max(stylo_ai_score, 0.05), 0.98)


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
        # ── 1. TF-IDF Vocabulary Signal ─────────────────────────────────────
        text_vector = ml.text_vectorizer.transform([text])
        probs       = ml.text_model.predict_proba(text_vector)[0]
        prob_human_tfidf = float(probs[0])
        prob_ai_tfidf    = float(probs[1])

        # ── 2. Structural Generalization Signal ─────────────────────────────
        prob_ai_stylo = calculate_generalization_signals(text)

        # ── 3. Weighted Fusion (65% ML Model + 35% Structural Generalization)
        if word_count >= 15:
            final_prob_ai = (0.65 * prob_ai_tfidf) + (0.35 * prob_ai_stylo)
        else:
            final_prob_ai = (0.80 * prob_ai_tfidf) + (0.20 * prob_ai_stylo)

        final_prob_human = 1.0 - final_prob_ai

        is_ai  = final_prob_ai >= 0.5
        result = "AI-Generated" if is_ai else "Human Written"

        prob_ai_pct    = round(final_prob_ai    * 100, 1)
        prob_human_pct = round(final_prob_human * 100, 1)
        confidence     = prob_ai_pct if is_ai else prob_human_pct

        # ── 4. Sentence-level analysis ──────────────────────────────────────
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) >= 3]
        sentences = sentences[:15]

        sentence_scores = []
        if sentences:
            sent_vectors = ml.text_vectorizer.transform(sentences)
            sent_probs   = ml.text_model.predict_proba(sent_vectors)[:, 1]
            for s, p in zip(sentences, sent_probs):
                sentence_scores.append({
                    "text":    s,
                    "ai_prob": round(float(p), 4)
                })

        # ── 5. Confidence label ─────────────────────────────────────────────
        if confidence >= 85:
            confidence_label = "Very High"
        elif confidence >= 70:
            confidence_label = "High"
        elif confidence >= 55:
            confidence_label = "Moderate"
        else:
            confidence_label = "Low"

        # ── 6. Save result to database ──────────────────────────────────────
        try:
            user_id = getattr(request, 'user', {}).get('uid', 'anonymous')
            scan_data = {
                "id":               str(uuid.uuid4()),
                "scan_type":        "Text",
                "target_name":      f"Text Snippet ({word_count} words)",
                "is_ai":            is_ai,
                "confidence":       confidence,
                "prob_ai":          prob_ai_pct,
                "prob_human":       prob_human_pct,
                "confidence_label": confidence_label,
                "prediction":       result,
                "word_count":       word_count,
                "timestamp":        datetime.utcnow().isoformat(),
            }
            collection = f"text_results_{user_id}"
            external_db.create_document(collection, scan_data)
        except Exception as db_err:
            print(f"[text_routes] DB save failed (non-fatal): {db_err}")

        return jsonify({
            "prediction":       result,
            "is_ai":            is_ai,
            "confidence":       confidence,
            "confidence_label": confidence_label,
            "prob_human":       prob_human_pct,
            "prob_ai":          prob_ai_pct,
            "word_count":       word_count,
            "sentences":        sentence_scores,
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
