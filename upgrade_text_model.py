import os
import re

inference_path = r'D:\Server\ai-training-panel\python_engine\inference.py'

with open(inference_path, 'r', encoding='utf-8') as f:
    content = f.read()

text_new = '''def run_text_inference(file_path):
    try:
        import torch
        from transformers import pipeline
        global hf_text_pipe
        
        # We lazy-load the State-of-the-Art RoBERTa deepfake text detector
        if 'hf_text_pipe' not in globals() or hf_text_pipe is None:
            print("[SOTA] Initializing HuggingFace RoBERTa for AI Text Detection...")
            device = 0 if torch.cuda.is_available() else -1
            hf_text_pipe = pipeline('text-classification', model='roberta-base-openai-detector', device=device)

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read().strip()

        if not text:
            return {"error": "Text file is empty."}

        # HuggingFace RoBERTa has a 512 token limit (about 400 words)
        # To handle unlimited text, we will split the text into chunks of 400 words
        words = text.split()
        chunk_size = 400
        chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        
        if not chunks:
             return {"error": "No valid words found."}
             
        # Run inference on all chunks
        print(f"[SOTA] Analyzing {len(chunks)} text chunks...")
        results = hf_text_pipe(chunks)
        
        # Results look like [{'label': 'Fake', 'score': 0.99}, ...]
        # We average the scores
        total_fake_score = 0
        for res in results:
            if 'Fake' in res['label']:
                total_fake_score += res['score']
            else:
                total_fake_score += (1.0 - res['score'])
                
        avg_fake_score = total_fake_score / len(chunks)
        
        is_ai = bool(avg_fake_score >= 0.5)
        confidence = float(avg_fake_score * 100) if is_ai else float((1.0 - avg_fake_score) * 100)

        return {
            "is_ai": is_ai,
            "confidence": round(confidence, 1),
            "model": "HuggingFace RoBERTa (SOTA Chunking)",
            "details": f"Analyzed {len(chunks)} chunks of text for maximum accuracy"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
'''

content = re.sub(r'def run_text_inference\(file_path\):.*?return \{.*?\}', text_new, content, flags=re.DOTALL)

with open(inference_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully upgraded text inference to HuggingFace RoBERTa!")
