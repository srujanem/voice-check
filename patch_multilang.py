import os

file_path = r"D:\voice-check\voice-check\backend\routes\text_routes.py"
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
in_predict = False
skip_predict = False

for line in lines:
    if line.startswith("import re") and "langdetect" not in "".join(lines):
        out.append(line)
        out.append("from langdetect import detect\n")
        out.append("from deep_translator import GoogleTranslator\n")
        continue

    if "@text_bp.route(\"/predict_text\"" in line:
        in_predict = True
    
    if in_predict and "def predict_text():" in line:
        out.append(line)
        # We will write our own predict_text logic now, and skip the rest until @text_bp.route("/reload_text_model")
        skip_predict = True
        
        # Inject our new logic
        out.append('''
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

        # 5. Confidence label
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
            "translated_from":  detected_lang if is_foreign else None
        })

    except Exception as e:
        print(f"[text_routes] Error processing text: {e}")
        return jsonify({"error": "Failed to process text. Please try again."}), 500
''')
        continue

    if skip_predict:
        if "@text_bp.route(\"/reload_text_model\"" in line:
            skip_predict = False
            out.append(line)
        continue
        
    out.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(out)
print("Patch successfully applied!")
