from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict_voice', methods=['POST'])
def pv():
    f = request.files.get('audio')
    return jsonify({
        "prediction": "AI Voice",
        "confidence": 99.0,
        "prob_human": 1.0,
        "prob_ai": 99.0,
        "filename": f.filename if f else "None"
    })

@app.route('/api/infer', methods=['POST'])
def api_infer():
    file = request.files.get("file")
    req_type = request.form.get("type", "voice")
    
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
        
    client = app.test_client()
    file_content = file.read()
    
    import io
    response = client.post(
        '/predict_voice',
        data={'audio': (io.BytesIO(file_content), file.filename)},
        content_type='multipart/form-data'
    )
    
    data = response.get_json()
    is_ai = "ai" in str(data.get("prediction", "")).lower()
    conf_val = float(data.get("prob_ai", 0.0)) / 100.0
    
    return jsonify({
        "is_ai": is_ai,
        "confidence": conf_val,
        "filename": data.get("filename")
    })

if __name__ == "__main__":
    with app.test_client() as c:
        import io
        r = c.post('/api/infer', data={'file': (io.BytesIO(b"dummy data"), "test.mp3"), 'type': 'voice'})
        print(r.get_json())
