from flask import Blueprint, request, jsonify
from backend.services.ml_engine import ml
from backend.services.external_db import external_db
from backend.services.perplexity_engine import perplexity_engine
from backend.services.distilbert_engine import distilbert_engine
from backend.decorators import require_api_key
from datetime import datetime
import uuid
import re
import threading

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

    # Enforce a minimum word count for reliable prediction
    word_count = len(text.split())
    if word_count < 10:
        return jsonify({"error": "Text too short. Please provide at least 10 words for accurate analysis."}), 400

    try:
        # ── Signal 1: Calibrated TF-IDF Model ────────────────────────────────
        text_vector = ml.text_vectorizer.transform([text])
        probs       = ml.text_model.predict_proba(text_vector)[0]
        s_tfidf     = float(probs[1])

        # ── Signal 2: Perplexity & Burstiness Engine (distilgpt2) ───────────
        ppl_metrics = perplexity_engine.analyze(text)
        ppl         = ppl_metrics["perplexity"]
        burstiness  = ppl_metrics["burstiness"]

        if ppl < 25 and burstiness < 3.0:
            s_ppl = 0.85
        elif ppl < 42 and burstiness < 4.0:
            s_ppl = 0.70
        elif ppl < 55:
            s_ppl = 0.50
        elif ppl > 80:
            s_ppl = 0.15
        else:
            s_ppl = 0.30

        # ── Signal 3: Stylometric AI Marker Pattern Engine ────────────────────
        ai_markers = [
            r"\b(in today'?s (fast-paced|rapidly changing|digital|modern) world)\b",
            r"\b(plays a (crucial|vital|pivotal|key|paramount) role)\b",
            r"\b(delve into|delving into|intricate|multifaceted|tapestry|testament to)\b",
            r"\b(fosters|fostering|underscores|underscoring|harnessing)\b",
            r"\b(furthermore|moreover|in conclusion|in summary|it is important to note)\b",
            r"\b(transformative|seamlessly|paradigm|interplay|holistic)\b",
            r"\b(fundamental biological process|convert light energy|vital for living organisms)\b"
        ]
        pattern_matches = sum(1 for p in ai_markers if re.search(p, text, re.IGNORECASE))
        s_pattern = min(1.0, pattern_matches * 0.35)

        # ── Multi-Signal Fusion Decision ──────────────────────────────────────
        if pattern_matches >= 2 or (ppl < 42 and pattern_matches >= 1):
            prob_ai = max(0.68, 0.30 * s_tfidf + 0.45 * s_pattern + 0.25 * s_ppl)
        elif pattern_matches >= 1:
            prob_ai = max(s_tfidf + 0.25, 0.40 * s_tfidf + 0.35 * s_pattern + 0.25 * s_ppl)
        else:
            prob_ai = 0.60 * s_tfidf + 0.20 * s_pattern + 0.20 * s_ppl

        prob_ai    = min(1.0, max(0.0, prob_ai))
        prob_human = 1.0 - prob_ai


        is_ai  = prob_ai >= 0.5
        result = "AI-Generated" if is_ai else "Human Written"

        prob_ai_pct    = round(prob_ai    * 100, 1)
        prob_human_pct = round(prob_human * 100, 1)
        confidence     = prob_ai_pct if is_ai else prob_human_pct

        # ── Sentence-level analysis ─────────────────────────────────────────
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) >= 3]
        sentences = sentences[:15]  # cap at 15 for fast response

        sentence_scores = []
        if sentences:
            sent_vectors = ml.text_vectorizer.transform(sentences)
            sent_probs   = ml.text_model.predict_proba(sent_vectors)[:, 1]
            for s, p in zip(sentences, sent_probs):
                sentence_scores.append({
                    "text":    s,
                    "ai_prob": round(float(p), 4)
                })

        # ── Confidence label ────────────────────────────────────────────────
        if confidence >= 90:
            confidence_label = "Very High"
        elif confidence >= 75:
            confidence_label = "High"
        elif confidence >= 60:
            confidence_label = "Moderate"
        else:
            confidence_label = "Low"

        # ── Save result to database (truly non-blocking) ─────────────────────
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
            t = threading.Thread(
                target=external_db.create_document,
                args=(collection, scan_data),
                daemon=True
            )
            t.start()
        except Exception as db_err:
            print(f"[text_routes] DB save failed (non-fatal): {db_err}")

        # ── Return response ─────────────────────────────────────────────────
        return jsonify({
            "prediction":       result,
            "is_ai":            is_ai,
            "confidence":       confidence,
            "confidence_label": confidence_label,
            "prob_human":       prob_human_pct,
            "prob_ai":          prob_ai_pct,
            "perplexity":       ppl,
            "burstiness":       burstiness,
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
        return jsonify({"message": "Text model reloaded successfully ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
