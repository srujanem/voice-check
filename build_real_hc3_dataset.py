import os
import glob
import pandas as pd

print("Downloading real HC3 (Human vs ChatGPT) Parquet dataset...")
parquet_url = "https://huggingface.co/api/datasets/Hello-SimpleAI/HC3/parquet/all/train/0.parquet"

df = pd.read_parquet(parquet_url)
print(f"Loaded HC3 Parquet dataframe with {len(df)} Q&A items.")

human_dir = os.path.join("dataset_text", "human")
ai_dir    = os.path.join("dataset_text", "ai")

print("Clearing old synthetic dataset files...")
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

print(f"Generating {TARGET} real human text samples and {TARGET} real ChatGPT text samples...")

for idx, row in df.iterrows():
    human_ans = row["human_answers"]
    chat_ans  = row["chatgpt_answers"]

    try:
        for ha in human_ans:
            if human_count >= TARGET:
                break
            txt = str(ha).strip()
            if len(txt.split()) >= 15:
                human_count += 1
                with open(os.path.join(human_dir, f"{human_count}.txt"), "w", encoding="utf-8", errors="ignore") as fp:
                    fp.write(txt)
    except Exception:
        pass

    try:
        for ca in chat_ans:
            if ai_count >= TARGET:
                break
            txt = str(ca).strip()
            if len(txt.split()) >= 15:
                ai_count += 1
                with open(os.path.join(ai_dir, f"{ai_count}.txt"), "w", encoding="utf-8", errors="ignore") as fp:
                    fp.write(txt)
    except Exception:
        pass

    if human_count >= TARGET and ai_count >= TARGET:
        break

print(f"Successfully generated {human_count} REAL Human files and {ai_count} REAL ChatGPT AI files.")
