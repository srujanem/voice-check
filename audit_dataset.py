import os
import glob

def calculate_formality(text):
    text = " " + text.lower() + " "
    words = text.split()
    if len(words) < 5: return False
    
    avg_word_length = sum(len(w) for w in words) / len(words)
    
    casual_words = [" i ", " me ", " my ", " you ", " your ", " yeah ", " cool ", " stuff ", " gonna ", " wanna ", " didn't ", " haven't ", " i'm "]
    formal_words = [" therefore ", " furthermore ", " moreover ", " consequently ", " thus ", " crucial ", " essential ", " multifaceted ", " tapestry ", " fast-paced ", " significant ", " analysis ", " implement "]
    
    casual_score = sum(text.count(w) for w in casual_words)
    formal_score = sum(text.count(w) for w in formal_words)
    
    # Simple heuristic classification
    if formal_score > casual_score or avg_word_length >= 5.5:
        return True
    return False

def audit_folder(path):
    base_dir = r"D:\voice-check\voice-check"
    full_path = os.path.join(base_dir, path)
    files = glob.glob(os.path.join(full_path, "**", "*.txt"), recursive=True)
    
    formal_count = 0
    total_count = 0
    
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
                text = fp.read().strip()
            if len(text.split()) >= 8:
                total_count += 1
                if calculate_formality(text):
                    formal_count += 1
        except:
            pass
    return formal_count, total_count

ai_paths = [r"dataset_text\ai", r"dataset_text\ai_generated"]
human_paths = [r"dataset_text\human"]

ai_formal, ai_total = 0, 0
for p in ai_paths:
    f, t = audit_folder(p)
    ai_formal += f
    ai_total += t
    
human_formal, human_total = 0, 0
for p in human_paths:
    f, t = audit_folder(p)
    human_formal += f
    human_total += t
    
print("--- STYLE AUDIT RESULTS ---")
print(f"AI Texts   : {ai_formal} Formal out of {ai_total} Total ({ai_formal/ai_total*100:.2f}%)")
print(f"Human Texts: {human_formal} Formal out of {human_total} Total ({human_formal/human_total*100:.2f}%)")

if (human_formal/human_total) > (ai_formal/ai_total):
    print("FLAG: Your model is likely learning that 'Formal = Human'.")
else:
    print("FLAG: Your model is likely learning that 'Formal = AI'.")
