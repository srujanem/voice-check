from flask import Blueprint, request, jsonify
from backend.services.ml_engine import ml
from backend.services.external_db import external_db
from backend.decorators import require_api_key
from datetime import datetime
import uuid
import re

text_bp = Blueprint('text', __name__)

# Stylometric AI Vocabulary & Phrase Indicators
AI_MARKER_PATTERNS = [
    r"\b(in today'?s (fast-paced|rapidly changing|digital|modern) world)\b",
    r"\b(plays a (crucial|vital|pivotal|key|paramount) role)\b",
    r"\b(delve into|delving into|intricate|multifaceted|tapestry|testament to)\b",
    r"\b(fosters|fostering|underscores|underscoring|harnessing)\b",
    r"\b(furthermore|moreover|in conclusion|in summary|it is important to note)\b",
    r"\b(transformative|seamlessly|paradigm|interplay|holistic)\b"
]


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
        # ── 1. Model Prediction ─────────────────────────────────────────────
        text_vector = ml.text_vectorizer.transform([text])
        probs       = ml.text_model.predict_proba(text_vector)[0]
        prob_human  = float(probs[0])
        prob_ai     = float(probs[1])

        # ── 2. AI Stylometric Pattern Adjustment ────────────────────────────
        text_lower = text.lower()
        matched_markers = 0
        for pattern in AI_MARKER_PATTERNS:
            if re.search(pattern, text_lower):
                matched_markers += 1

        if matched_markers >= 2:
            prob_ai = max(prob_ai, 0.85)
            prob_human = 1.0 - prob_ai
        elif matched_markers == 1:
            prob_ai = max(prob_ai, 0.70)
            prob_human = 1.0 - prob_ai

        is_ai  = prob_ai >= 0.5
        result = "AI-Generated" if is_ai else "Human Written"

        prob_ai_pct    = round(prob_ai    * 100, 1)
        prob_human_pct = round(prob_human * 100, 1)
        confidence     = prob_ai_pct if is_ai else prob_human_pct

        # ── 3. Sentence-level analysis ──────────────────────────────────────
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

        # ── 4. Confidence label ─────────────────────────────────────────────
        if confidence >= 85:
            confidence_label = "Very High"
        elif confidence >= 70:
            confidence_label = "High"
        elif confidence >= 55:
            confidence_label = "Moderate"
        else:
            confidence_label = "Low"

        # ── 5. Database logging ─────────────────────────────────────────────
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
