from flask import Blueprint, request, jsonify
import re
from urllib.parse import urlparse
from backend.services.ml_engine import ml
from backend.decorators import require_api_key

url_bp = Blueprint('url', __name__)

_PRIVATE_IP_RE = re.compile(
    r'^(127\.\d+\.\d+\.\d+|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|localhost)$',
    re.IGNORECASE,
)

@url_bp.route("/predict_url", methods=["POST"])
@require_api_key
def predict_url():
    if ml.text_model is None or ml.text_vectorizer is None:
        return jsonify({"error": "Text model not loaded"}), 500

    data = request.json
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    if not url.startswith("http://") and not url.startswith("https://"):
        return jsonify({"error": "Invalid URL scheme. Only http and https are allowed."}), 400

    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    if _PRIVATE_IP_RE.match(hostname):
        return jsonify({"error": "Access to private/internal addresses is not allowed."}), 400

    try:
        import urllib.request
        from bs4 import BeautifulSoup
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=10).read()
        soup = BeautifulSoup(html, 'html.parser')
        
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        text = soup.get_text(separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        if len(text) < 50:
            return jsonify({"error": "Not enough meaningful text found on this page."}), 400
            
        text = text[:5000]
        text_vector = ml.text_vectorizer.transform([text])
        prob_ai = float(ml.text_model.predict_proba(text_vector)[0][1])
        
        is_ai = prob_ai >= 0.5
        result = "AI-Generated" if is_ai else "Human Written"
        
        prob_ai_pct = round(prob_ai * 100, 1)
        prob_human_pct = round((1.0 - prob_ai) * 100, 1)
        confidence = prob_ai_pct if is_ai else prob_human_pct
        
        return jsonify({
            "prediction": result,
            "confidence": confidence,
            "prob_human": prob_human_pct,
            "prob_ai": prob_ai_pct,
            "extracted_text_preview": text[:200] + "..."
        })
    except Exception as e:
        print(f"URL Prediction Error: {e}")
        return jsonify({"error": "Failed to scrape URL. Access denied or protected."}), 500
