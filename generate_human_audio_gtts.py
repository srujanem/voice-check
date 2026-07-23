import os
import pdfplumber
import glob
from gtts import gTTS
import time

# Find the latest uploaded PDF
uploaded_dir = r'C:\Users\sruja\.gemini\antigravity\brain\656ffd67-2c5d-4c4e-a46e-fd5792eed8db\.user_uploaded'
pdf_files = glob.glob(os.path.join(uploaded_dir, '*.pdf'))
pdf_files.sort(key=os.path.getmtime, reverse=True)
latest_pdf = pdf_files[0]
print(f"Using PDF: {latest_pdf}")

# Extract text from the PDF
text = ""
try:
    with pdfplumber.open(latest_pdf) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
except Exception as e:
    print(f"Error reading PDF: {e}")

words = text.split()
chunk_size = 40  # shorter chunks for audio

chunks = []
for i in range(0, len(words), chunk_size):
    chunk = " ".join(words[i:i+chunk_size])
    if len(chunk.split()) >= 10:
        chunks.append(chunk)

output_dir = r"c:\voice-check\dataset\human"
os.makedirs(output_dir, exist_ok=True)

# Find the max index to continue naming
existing_files = [f for f in os.listdir(output_dir) if f.endswith('.wav') or f.endswith('.mp3')]
max_idx = 0
for f in existing_files:
    try:
        idx = int(f.split('.')[0])
        if idx > max_idx:
            max_idx = idx
    except ValueError:
        pass

generated = 0
target = 100

print(f"Starting to generate 100 audio files using gTTS in {output_dir}...")
for i, chunk in enumerate(chunks):
    if generated >= target:
        break
    
    current_idx = max_idx + 1 + i
    out_path = os.path.join(output_dir, f"{current_idx}.mp3")
    
    try:
        tts = gTTS(text=chunk, lang='en', slow=False)
        tts.save(out_path)
        generated += 1
        if generated % 10 == 0:
            print(f"  Generated {generated} / {target} files...")
        time.sleep(0.5) # Prevent rate limiting
    except Exception as e:
        print(f"Error generating TTS for chunk {i}: {e}")
        time.sleep(2)

print("Done generating 100 audio files!")
