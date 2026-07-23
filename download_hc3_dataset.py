import os
import glob
import json
import requests
from datasets import load_dataset

print("Downloading HC3 dataset...")

human_dir = os.path.join("dataset_text", "human")
ai_dir    = os.path.join("dataset_text", "ai")

# Clean existing repetitive text files
print("Clearing old synthetic/repetitive text dataset...")
for f in glob.glob(os.path.join(human_dir, "*.txt")):
    try: os.remove(f)
    except Exception: pass
for f in glob.glob(os.path.join(ai_dir, "*.txt")):
    try: os.remove(f)
    except Exception: pass

os.makedirs(human_dir, exist_ok=True)
os.makedirs(ai_dir, exist_ok=True)

try:
    # Try trust_remote_code=True first
    ds = load_dataset("Hello-SimpleAI/HC3", "all", split="train", trust_remote_code=True)
    items = ds
except Exception as e:
    print(f"HuggingFace dataset load fallback: {e}")
    # Fallback to direct jsonl download from HF repository
    url = "https://huggingface.co/datasets/Hello-SimpleAI/HC3/resolve/main/all.jsonl"
    r = requests.get(url, stream=True)
    lines = r.iter_lines()
    items = []
    for line in lines:
        if line:
            items.append(json.loads(line.decode('utf-8')))
            if len(items) >= 10000:
                break

human_count = 0
ai_count    = 0
TARGET      = 5000

print(f"Processing dataset items to create {TARGET} real human + {TARGET} real ChatGPT files...")

for item in items:
    human_answers = item.get("human_answers", [])
    chatgpt_answers = item.get("chatgpt_answers", [])

    for ha in human_answers:
        if human_count >= TARGET:
            break
        txt = ha.strip()
        if len(txt.split()) >= 15:
            human_count += 1
            with open(os.path.join(human_dir, f"{human_count}.txt"), "w", encoding="utf-8", errors="ignore") as fp:
                fp.write(txt)

    for ca in chatgpt_answers:
        if ai_count >= TARGET:
            break
        txt = ca.strip()
        if len(txt.split()) >= 15:
            ai_count += 1
            with open(os.path.join(ai_dir, f"{ai_count}.txt"), "w", encoding="utf-8", errors="ignore") as fp:
                fp.write(txt)

    if human_count >= TARGET and ai_count >= TARGET:
        break

print(f"Success! Created {human_count} REAL Human samples and {ai_count} REAL ChatGPT AI samples.")
