import PyPDF2
import requests

url = "http://localhost:5000/api/infer"

def test_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for i in range(min(2, len(reader.pages))):
                text += reader.pages[i].extract_text() + "\n"
                
        if not text.strip(): return
        print(f"\n--- Testing {pdf_path} ---")
        # Try local flask server
        try:
            r = requests.post("http://localhost:5000/predict_text", json={"text": text})
            print("Local Flask (/predict_text) Response:")
            data = r.json()
            print(f"Prediction: {data.get('prediction')} (AI: {data.get('prob_ai')}%, Human: {data.get('prob_human')}%)")
        except Exception as e:
            print("Could not reach local flask server:", e)
            
    except Exception as e:
        pass

import glob
pdf_files = glob.glob(r"C:\Users\sruja\.gemini\antigravity\brain\656ffd67-2c5d-4c4e-a46e-fd5792eed8db\.user_uploaded\*.pdf")
for f in pdf_files[-5:]:
    test_pdf(f)
