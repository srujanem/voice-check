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
        # ── Overall prediction (Ensemble ML) ────────────────────────────────
        text_vector = ml.text_vectorizer.transform([text])
        probs       = ml.text_model.predict_proba(text_vector)[0]
        prob_ai_ml  = float(probs[1])

        # ── Perplexity & Burstiness Engine (Option 2) ────────────────────────
        ppl_metrics = perplexity_engine.analyze(text)
        ppl         = ppl_metrics["perplexity"]
        burstiness  = ppl_metrics["burstiness"]

        # Perplexity score adjustment (low PPL < 50 indicates AI, high PPL > 75 indicates Human)
        if ppl < 40:
            ppl_ai_score = 0.95
        elif ppl < 55:
            ppl_ai_score = 0.80
        elif ppl > 80:
            ppl_ai_score = 0.10
        elif ppl > 65:
            ppl_ai_score = 0.25
        else:
            ppl_ai_score = 0.50

        # Burstiness adjustment (low burstiness < 4.0 indicates uniform AI structure)
        if burstiness < 4.0 and word_count >= 20:
            ppl_ai_score = min(1.0, ppl_ai_score + 0.15)
        elif burstiness > 8.0:
            ppl_ai_score = max(0.0, ppl_ai_score - 0.15)

        # ── DistilBERT Engine (Option A — 98% accuracy) ──────────────────
        bert_result = distilbert_engine.predict(text)

        # ── Three-Way Fusion ─────────────────────────────────────────────
        if bert_result is not None:
            # 40% XGBoost + 30% Perplexity + 30% DistilBERT
            prob_ai = (
                0.40 * prob_ai_ml +
                0.30 * ppl_ai_score +
                0.30 * bert_result["prob_ai"]
            )
        else:
            # Fallback: 50% XGBoost + 50% Perplexity
            prob_ai = (0.50 * prob_ai_ml) + (0.50 * ppl_ai_score)

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
