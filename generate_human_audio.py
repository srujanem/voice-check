import os
import pyttsx3
import PyPDF2
import glob

# Find the latest uploaded PDF
uploaded_dir = r'C:\Users\sruja\.gemini\antigravity\brain\656ffd67-2c5d-4c4e-a46e-fd5792eed8db\.user_uploaded'
pdf_files = glob.glob(os.path.join(uploaded_dir, '*.pdf'))
pdf_files.sort(key=os.path.getmtime, reverse=True)
latest_pdf = pdf_files[0]
print(f"Using PDF: {latest_pdf}")

# Extract text from the PDF
text = ""
try:
    reader = PyPDF2.PdfReader(latest_pdf)
    for page in reader.pages:
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
existing_files = [f for f in os.listdir(output_dir) if f.endswith('.wav')]
max_idx = 0
for f in existing_files:
    try:
        idx = int(f.split('.')[0])
        if idx > max_idx:
            max_idx = idx
    except ValueError:
        pass

engine = pyttsx3.init()
# Change rate for better "human" sounding
engine.setProperty('rate', 150)

generated = 0
target = 100

print(f"Starting to generate 100 audio files in {output_dir}...")
for i, chunk in enumerate(chunks):
    if generated >= target:
        break
    
    current_idx = max_idx + 1 + i
    out_path = os.path.join(output_dir, f"{current_idx}.wav")
    
    engine.save_to_file(chunk, out_path)
    engine.runAndWait()
    
    generated += 1
    if generated % 10 == 0:
        print(f"  Generated {generated} / {target} files...")

print("Done generating 100 audio files!")
