import requests
import glob

pdf_files = glob.glob(r"C:\Users\sruja\.gemini\antigravity\brain\656ffd67-2c5d-4c4e-a46e-fd5792eed8db\.user_uploaded\*.pdf")
pdf_path = pdf_files[-1] if pdf_files else None

if not pdf_path:
    print("No PDFs found.")
    exit(1)

print(f"Testing with {pdf_path}")
url = "http://localhost:5000/api/infer"

with open(pdf_path, 'rb') as f:
    files = {'file': (pdf_path.split('\\')[-1], f, 'application/pdf')}
    data = {'type': 'text'}
    
    try:
        r = requests.post(url, files=files, data=data)
        print("Status:", r.status_code)
        try:
            print("Response:", r.json())
        except:
            print("Text:", r.text[:200])
    except Exception as e:
        print("Error:", e)
