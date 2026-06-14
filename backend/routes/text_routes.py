from flask import Blueprint, request, jsonify
from backend.services.ml_engine import ml
from backend.decorators import require_api_key
import re

text_bp = Blueprint('text', __name__)

@text_bp.route("/predict_text", methods=["POST"])
@require_api_key
def predict_text():
    if ml.text_model is None or ml.text_vectorizer is None:
        return jsonify({"error": "Text model not loaded"}), 500

    data = request.json
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data["text"].strip()
    if not text:
        return jsonify({"error": "Empty text"}), 400

    try:
        text_vector = ml.text_vectorizer.transform([text])
        prob_ai = float(ml.text_model.predict_proba(text_vector)[0][1])
        
        is_ai = prob_ai >= 0.5
        result = "AI-Generated" if is_ai else "Human Written"
        
        prob_ai_pct = round(prob_ai * 100, 1)
        prob_human_pct = round((1.0 - prob_ai) * 100, 1)
        confidence = prob_ai_pct if is_ai else prob_human_pct

        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        sentence_scores = []
        if sentences:
            sentence_vectors = ml.text_vectorizer.transform(sentences)
            sentence_probs = ml.text_model.predict_proba(sentence_vectors)[:, 1]
            for s, p in zip(sentences, sentence_probs):
                sentence_scores.append({
                    "text": s,
                    "ai_prob": float(p)
                })

        return jsonify({
            "prediction": result,
            "confidence": confidence,
            "prob_human": prob_human_pct,
            "prob_ai": prob_ai_pct,
            "sentences": sentence_scores
        })
    except Exception as e:
        print(f"Error processing text: {e}")
        return jsonify({"error": "Failed to process text"}), 500
