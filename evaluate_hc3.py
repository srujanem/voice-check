import pandas as pd
import joblib

vec = joblib.load("text_vectorizer.pkl")
model = joblib.load("text_model.pkl")

url = "https://huggingface.co/api/datasets/Hello-SimpleAI/HC3/parquet/all/train/0.parquet"
df = pd.read_parquet(url)

# Take samples from the end (index 15000+) that were NOT in the training set
test_df = df.iloc[15000:15200]

human_correct = 0
human_total   = 0
ai_correct    = 0
ai_total      = 0

for _, row in test_df.iterrows():
    h_list = row["human_answers"]
    c_list = row["chatgpt_answers"]
    
    try:
        for h in h_list[:1]:
            txt = str(h).strip()
            if len(txt.split()) >= 15:
                feat = vec.transform([txt])
                pred = model.predict(feat)[0]
                if pred == 0: human_correct += 1
                human_total += 1
    except Exception: pass

    try:
        for c in c_list[:1]:
            txt = str(c).strip()
            if len(txt.split()) >= 15:
                feat = vec.transform([txt])
                pred = model.predict(feat)[0]
                if pred == 1: ai_correct += 1
                ai_total += 1
    except Exception: pass

print("=" * 60)
print("  EVALUATION ON UNSEEN REAL HC3 DATASET")
print("=" * 60)
print(f"Human Accuracy: {human_correct}/{human_total} ({human_correct/max(1,human_total)*100:.1f}%)")
print(f"AI Accuracy   : {ai_correct}/{ai_total} ({ai_correct/max(1,ai_total)*100:.1f}%)")
print(f"Overall Acc   : {(human_correct+ai_correct)/(human_total+ai_total)*100:.1f}%")
