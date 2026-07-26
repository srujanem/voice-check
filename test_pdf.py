import PyPDF2
import joblib
import sys
import glob
import os

try:
    vectorizer = joblib.load("text_vectorizer.pkl")
    model = joblib.load("text_model.pkl")
except Exception as e:
    print(f"Error loading model: {e}")
    sys.exit(1)

# Find all user uploaded pdfs
pdf_dir = r"C:\Users\sruja\.gemini\antigravity\brain\656ffd67-2c5d-4c4e-a46e-fd5792eed8db\.user_uploaded"
pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
# Get the 3 most recent
pdf_files.sort(key=os.path.getmtime, reverse=True)
recent_pdfs = pdf_files[:3]

for pdf_path in recent_pdfs:
    print(f"\n--- Testing PDF: {os.path.basename(pdf_path)} ---")
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for i in range(min(2, len(reader.pages))): # just first 2 pages
                text += reader.pages[i].extract_text() + "\n"
        
        # Test full text
        if not text.strip():
            print("No text found.")
            continue
            
        print(f"Extracted Text Snippet: {text[:200].replace(chr(10), ' ')}...")
        v = vectorizer.transform([text])
        p = model.predict_proba(v)[0]
        print(f"Prediction -> Human: {p[0]:.4f} | AI: {p[1]:.4f}")
        
    except Exception as e:
        print(f"Error reading PDF: {e}")
