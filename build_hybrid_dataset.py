import os
import glob
import pandas as pd
import pdfplumber
import random

print("Building hybrid dataset (HC3 Real Q&A + NCERT Academic Text)...")
parquet_url = "https://huggingface.co/api/datasets/Hello-SimpleAI/HC3/parquet/all/train/0.parquet"

df = pd.read_parquet(parquet_url)
print(f"Loaded HC3 Parquet dataframe with {len(df)} items.")

human_dir = os.path.join("dataset_text", "human")
ai_dir    = os.path.join("dataset_text", "ai")

print("Clearing old text files...")
for f in glob.glob(os.path.join(human_dir, "*.txt")):
    try: os.remove(f)
    except Exception: pass

for f in glob.glob(os.path.join(ai_dir, "*.txt")):
    try: os.remove(f)
    except Exception: pass

os.makedirs(human_dir, exist_ok=True)
os.makedirs(ai_dir, exist_ok=True)

human_count = 0
ai_count    = 0
TARGET      = 5000

# Step 1: Add NCERT Academic Textbook chunks into Human dataset (so formal science is known as Human)
uploaded_dir = r'C:\Users\sruja\.gemini\antigravity\brain\656ffd67-2c5d-4c4e-a46e-fd5792eed8db\.user_uploaded'
pdf_files = glob.glob(os.path.join(uploaded_dir, '*.pdf'))

all_pdf_text = ""
for pdf_path in pdf_files:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                if txt: all_pdf_text += txt + "\n"
    except Exception: pass

words = all_pdf_text.split()
chunk_size = 70

pdf_chunks = []
for i in range(0, len(words), chunk_size):
    chunk = " ".join(words[i:i+chunk_size])
    if len(chunk.split()) >= 15:
        pdf_chunks.append(chunk)

print(f"Extracted {len(pdf_chunks)} formal academic human chunks from PDFs.")

for chunk in pdf_chunks:
    if human_count >= 1500: # 1500 formal academic human samples
        break
    human_count += 1
    with open(os.path.join(human_dir, f"{human_count}.txt"), "w", encoding="utf-8", errors="ignore") as fp:
        fp.write(chunk)

# Step 2: Add HC3 Human answers for the remaining human samples
for idx, row in df.iterrows():
    if human_count >= TARGET:
        break
    human_ans = row["human_answers"]
    try:
        for ha in human_ans:
            if human_count >= TARGET: break
            txt = str(ha).strip()
            if len(txt.split()) >= 15:
                human_count += 1
                with open(os.path.join(human_dir, f"{human_count}.txt"), "w", encoding="utf-8", errors="ignore") as fp:
                    fp.write(txt)
    except Exception: pass

# Step 3: Add HC3 ChatGPT answers for AI samples
for idx, row in df.iterrows():
    if ai_count >= TARGET:
        break
    chat_ans = row["chatgpt_answers"]
    try:
        for ca in chat_ans:
            if ai_count >= TARGET: break
            txt = str(ca).strip()
            if len(txt.split()) >= 15:
                ai_count += 1
                with open(os.path.join(ai_dir, f"{ai_count}.txt"), "w", encoding="utf-8", errors="ignore") as fp:
                    fp.write(txt)
    except Exception: pass

print(f"Done! Human samples: {human_count} (mix of formal academic + informal Q&A) | AI samples: {ai_count}")
