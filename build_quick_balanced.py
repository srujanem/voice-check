import os, glob, json, requests

human_dir = os.path.join("dataset_text", "human")
ai_dir    = os.path.join("dataset_text", "ai")

os.makedirs(human_dir, exist_ok=True)
os.makedirs(ai_dir, exist_ok=True)

for f in glob.glob(os.path.join(human_dir, "*.txt")):
    try: os.remove(f)
    except Exception: pass
for f in glob.glob(os.path.join(ai_dir, "*.txt")):
    try: os.remove(f)
    except Exception: pass

print("Fetching HC3 JSONL dataset...")
url = "https://huggingface.co/datasets/Hello-SimpleAI/HC3/resolve/main/all.jsonl"
r = requests.get(url, stream=True)

human_count = 0
ai_count = 0
TARGET = 2500

for line in r.iter_lines():
    if not line: continue
    item = json.loads(line.decode('utf-8', errors='ignore'))
    
    for ha in item.get("human_answers", []):
        if human_count >= TARGET: break
        txt = str(ha).strip()
        if len(txt.split()) >= 12:
            human_count += 1
            with open(os.path.join(human_dir, f"{human_count}.txt"), "w", encoding="utf-8", errors="ignore") as fp:
                fp.write(txt)
                
    for ca in item.get("chatgpt_answers", []):
        if ai_count >= TARGET: break
        txt = str(ca).strip()
        if len(txt.split()) >= 12:
            ai_count += 1
            with open(os.path.join(ai_dir, f"{ai_count}.txt"), "w", encoding="utf-8", errors="ignore") as fp:
                fp.write(txt)

    if human_count >= TARGET and ai_count >= TARGET:
        break

print(f"Dataset populated: {human_count} Human | {ai_count} AI files!")
