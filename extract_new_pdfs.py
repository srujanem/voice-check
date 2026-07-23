import os
import PyPDF2
import glob

uploaded_dir = r'C:\Users\sruja\.gemini\antigravity\brain\656ffd67-2c5d-4c4e-a46e-fd5792eed8db\.user_uploaded'
pdf_files = [
    os.path.join(uploaded_dir, 'media__1784796579081.pdf'),
    os.path.join(uploaded_dir, 'media__1784796589324.pdf')
]

output_dir = r"c:\voice-check\dataset_text\human"
os.makedirs(output_dir, exist_ok=True)

# Find the highest existing file index to continue from
existing_files = [f for f in os.listdir(output_dir) if f.endswith('.txt')]
max_idx = 1001
for f in existing_files:
    try:
        idx = int(f.split('.')[0])
        if idx > max_idx:
            max_idx = idx
    except ValueError:
        pass

current_idx = max_idx + 1

for pdf_file in pdf_files:
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        # Split text into chunks of ~80 words
        words = text.split()
        chunk_size = 80
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            # Only save chunks that are long enough
            if len(chunk.split()) > 20:
                out_path = os.path.join(output_dir, f"{current_idx}.txt")
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(chunk)
                current_idx += 1
                
        print(f"Successfully processed {os.path.basename(pdf_file)}")
    except Exception as e:
        print(f"Error processing {pdf_file}: {e}")

print(f"Finished. Extracted chunks up to index {current_idx - 1}")
