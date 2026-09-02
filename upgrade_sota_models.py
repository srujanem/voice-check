import os
import re

inference_path = r'D:\Server\ai-training-panel\python_engine\inference.py'

with open(inference_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Text Inference to use HuggingFace RoBERTa SOTA
text_new = '''
# Global HuggingFace pipelines for SOTA caching
hf_text_pipe = None
hf_image_pipe = None

def run_text_inference(text_data):
    try:
        import torch
        from transformers import pipeline
        global hf_text_pipe
        
        if hf_text_pipe is None:
            print("[SOTA] Initializing HuggingFace RoBERTa AI Detector (First run may take a moment to download)...")
            device = 0 if torch.cuda.is_available() else -1
            hf_text_pipe = pipeline('text-classification', model='roberta-base-openai-detector', device=device)
            
        print(f"[SOTA] Running Text Inference on GPU: {torch.cuda.is_available()}")
        result = hf_text_pipe(text_data[:512])[0]
        
        # roberta-base-openai-detector returns 'Real' or 'Fake'
        label = result['label'].lower()
        score = result['score'] * 100
        
        is_ai = (label == 'fake')
        # If it's Fake, confidence in AI is score. If Real, confidence in AI is 100-score.
        confidence = score if is_ai else (100 - score)
        
        return {
            "is_ai": bool(is_ai),
            "confidence": round(float(confidence), 1),
            "model": "HuggingFace RoBERTa (State-of-the-Art)",
            "details": f"Analyzed using roberta-base-openai-detector"
        }
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}
'''

content = re.sub(r'def run_text_inference\(text_data\):.*?return \{.*?\}', text_new, content, flags=re.DOTALL)


# 2. Update Image Inference to use HuggingFace ViT SOTA
image_new = '''def run_image_inference(file_path):
    try:
        import torch
        from transformers import pipeline
        global hf_image_pipe
        
        if hf_image_pipe is None:
            print("[SOTA] Initializing HuggingFace Vision Transformer for Deepfakes...")
            device = 0 if torch.cuda.is_available() else -1
            # Using a highly accurate ViT model fine-tuned for deepfake vs real
            hf_image_pipe = pipeline('image-classification', model='dima806/deepfake_vs_real_image_detection', device=device)
            
        print(f"[SOTA] Running Image Inference on GPU: {torch.cuda.is_available()}")
        # Predict
        results = hf_image_pipe(file_path)
        
        # Results is a list of dicts: [{'label': 'fake', 'score': 0.99}, ...]
        top_result = results[0]
        label = top_result['label'].lower()
        score = top_result['score'] * 100
        
        is_ai = ('fake' in label)
        confidence = score
        
        return {
            "is_ai": bool(is_ai),
            "confidence": round(float(confidence), 1),
            "model": "HuggingFace Vision Transformer (SOTA)",
            "details": f"Analyzed using dima806/deepfake_vs_real_image_detection"
        }
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}
'''

content = re.sub(r'def run_image_inference\(file_path\):.*?return \{.*?\}', image_new, content, flags=re.DOTALL)

with open(inference_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully upgraded inference.py to use HuggingFace State-of-the-Art models!")
