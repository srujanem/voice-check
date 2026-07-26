import os, glob, pdfplumber

pdf_dir = r'C:\Users\sruja\.gemini\antigravity\brain\656ffd67-2c5d-4c4e-a46e-fd5792eed8db\.user_uploaded'
human_dir = os.path.join("dataset_text", "human")

os.makedirs(human_dir, exist_ok=True)

pdf_files = [f for f in glob.glob(os.path.join(pdf_dir, '*.pdf')) if os.path.getsize(f) > 1000]

print(f"Extracting textbook passages from {len(pdf_files)} PDFs into dataset_text/human...")
count = 3000

for pdf_path in pdf_files:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:10]:
                txt = page.extract_text()
                if txt:
                    words = txt.split()
                    for i in range(0, len(words), 50):
                        chunk = " ".join(words[i:i+50])
                        if len(chunk.split()) >= 15:
                            count += 1
                            with open(os.path.join(human_dir, f"{count}.txt"), "w", encoding="utf-8", errors="ignore") as fp:
                                fp.write(chunk)
                            if count >= 4500:
                                break
    except Exception as e:
        pass
    if count >= 4500:
        break

print(f"Done! Created {count - 3000} textbook files in dataset_text/human.")
