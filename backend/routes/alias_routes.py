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

@alias_bp.route("/api/infer", methods=["POST"])
def api_infer():
    """Unified endpoint used by frontend UIs (text, voice, image, video)."""
    client = current_app.test_client()

    infer_type = request.form.get("type", "").lower()
    text_content = request.form.get("text", "").strip()

    file = request.files.get("file") or request.files.get("audio") or request.files.get("image") or request.files.get("video")

    # Determine type if omitted
    if not infer_type:
        if file:
            fn = file.filename.lower()
            if any(fn.endswith(ext) for ext in ['.wav', '.mp3', '.flac', '.webm', '.ogg', '.m4a']):
                infer_type = 'voice'
            elif any(fn.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp', '.bmp']):
                infer_type = 'image'
            elif any(fn.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
                infer_type = 'video'
            elif any(fn.endswith(ext) for ext in ['.txt']):
                infer_type = 'text'
        elif text_content:
            infer_type = 'text'

    if infer_type == 'text':
        if not text_content and file:
            try:
                text_content = file.read().decode('utf-8', errors='ignore').strip()
            except Exception:
                pass

        if not text_content:
            return jsonify({"error": "No text provided for analysis."}), 400

        res = client.post('/predict_text', json={"text": text_content})
        res_data = res.get_json() or {}

        if res.status_code != 200:
            return jsonify(res_data), res.status_code

        prob_ai = float(res_data.get("prob_ai", 50.0))
        prob_human = float(res_data.get("prob_human", 50.0))
        confidence = float(res_data.get("confidence", 50.0))
        prediction = res_data.get("prediction", "Human Written")

        return jsonify({
            "type": "text",
            "prediction": prediction,
            "is_ai": prob_ai >= 50.0,
            "prob_ai": prob_ai,
            "prob_human": prob_human,
            "confidence": confidence,
            "word_count": res_data.get("word_count", len(text_content.split())),
            "analysis": res_data
        })

    elif infer_type in ['voice', 'audio']:
        if not file:
            return jsonify({"error": "No audio file provided."}), 400
        file_content = file.read()
        res = client.post('/predict_voice', data={'audio': (io.BytesIO(file_content), file.filename)}, content_type='multipart/form-data')
        res_data = res.get_json() or {}

        if res.status_code != 200:
            return jsonify(res_data), res.status_code

        prob_ai = float(res_data.get("prob_ai", 50.0))
        prob_human = float(res_data.get("prob_human", 50.0))
        confidence = float(res_data.get("confidence", 50.0))
        prediction = res_data.get("prediction", "Authentic")

        return jsonify({
            "type": "voice",
            "prediction": prediction,
            "is_ai": prob_ai >= 50.0,
            "prob_ai": prob_ai,
            "prob_human": prob_human,
            "confidence": confidence,
            "analysis": res_data
        })

    elif infer_type == 'image':
        if not file:
            return jsonify({"error": "No image file provided."}), 400
        file_content = file.read()
        res = client.post('/predict_image', data={'image': (io.BytesIO(file_content), file.filename)}, content_type='multipart/form-data')
        res_data = res.get_json() or {}

        if res.status_code != 200:
            return jsonify(res_data), res.status_code

        prob_ai = float(res_data.get("prob_ai", 50.0))
        prob_human = float(res_data.get("prob_human", 50.0))
        confidence = float(res_data.get("confidence", 50.0))
        prediction = res_data.get("prediction", "Authentic")

        return jsonify({
            "type": "image",
            "prediction": prediction,
            "is_ai": prob_ai >= 50.0,
            "prob_ai": prob_ai,
            "prob_human": prob_human,
            "confidence": confidence,
            "analysis": res_data
        })

    elif infer_type == 'video':
        if not file:
            return jsonify({"error": "No video file provided."}), 400
        file_content = file.read()
        res = client.post('/predict_video', data={'video': (io.BytesIO(file_content), file.filename)}, content_type='multipart/form-data')
        return Response(res.data, status=res.status_code, headers=dict(res.headers))

    else:
        return jsonify({"error": f"Invalid inference type: '{infer_type}'"}), 400


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

