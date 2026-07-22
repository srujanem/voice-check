from flask import Blueprint, request, jsonify, Response, current_app
import io
import json

alias_bp = Blueprint('alias', __name__)

# Track API usage count
_usage_stats = {"total_calls": 0}
_webhooks = []

@alias_bp.before_app_request
def count_api_request():
    if request.path.startswith('/api/'):
        _usage_stats["total_calls"] += 1

@alias_bp.route("/api/scan-url", methods=["POST"])
def api_scan_url():
    client = current_app.test_client()
    data = request.json or {}
    res = client.post('/predict_url', json=data, headers={'Authorization': request.headers.get('Authorization', '')})
    res_data = res.get_json() or {}
    
    if res.status_code != 200:
        return jsonify(res_data), res.status_code
        
    pred_str = str(res_data.get("prediction", "")).lower()
    is_ai = "ai" in pred_str or "fake" in pred_str or "generated" in pred_str
    conf = float(res_data.get("confidence", 50.0)) / 100.0 if float(res_data.get("confidence", 50.0)) > 1.0 else float(res_data.get("confidence", 0.5))
    
    return jsonify({
        "is_ai": is_ai,
        "confidence": conf,
        "prob_ai": res_data.get("prob_ai"),
        "prob_human": res_data.get("prob_human"),
        "extracted_text_preview": res_data.get("extracted_text_preview")
    })

@alias_bp.route("/api/watermark", methods=["POST"])
def api_watermark():
    client = current_app.test_client()
    file = request.files.get("file") or request.files.get("image")
    if not file:
        return jsonify({"error": "No image file provided"}), 400
        
    file_content = file.read()
    res = client.post(
        '/create_watermark',
        data={'image': (io.BytesIO(file_content), file.filename)},
        content_type='multipart/form-data',
        headers={'Authorization': request.headers.get('Authorization', '')}
    )
    
    return Response(
        res.data,
        status=res.status_code,
        headers=dict(res.headers)
    )

@alias_bp.route("/api/usage", methods=["GET"])
def api_usage():
    return jsonify({"total_calls": _usage_stats["total_calls"]})

@alias_bp.route("/api/webhooks/register", methods=["POST"])
def api_register_webhook():
    data = request.json or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400
    if url not in _webhooks:
        _webhooks.append(url)
    return jsonify({"message": "Webhook registered successfully", "url": url}), 200
