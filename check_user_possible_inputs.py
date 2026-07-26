import joblib

vectorizer = joblib.load("text_vectorizer.pkl")
model      = joblib.load("text_model.pkl")

sentences = [
    ("Artificial Intelligence is transforming the world.", "AI"),
    ("Photosynthesis is the process by which plants make food.", "Human"),
    ("Furthermore, it is important to analyze the implications.", "AI"),
    ("I went to the market yesterday to buy some vegetables.", "Human"),
    ("The study of physics helps us understand energy and force.", "Human"),
    ("In conclusion, machine learning provides significant benefits.", "AI"),
    ("Global warming is caused by rising levels of carbon dioxide.", "AI/Human"),
    ("Cellular respiration produces ATP in mitochondria.", "Human"),
    ("AI detectors analyze perplexity and burstiness.", "AI"),
    ("The French Revolution started in 1789.", "Human"),
    ("Hello how are you doing today?", "Human"),
    ("This article explores the key factors influencing economic growth.", "AI"),
    ("Water boils at 100 degrees Celsius under normal pressure.", "Human"),
    ("In today's fast-paced world, technology plays a vital role.", "AI"),
    ("She wrote a letter to her friend in London.", "Human")
]

print("="*75)
print(f"{'Text Snippet':<55} | {'AI%':<6} | {'Verdict'}")
print("="*75)

for text, label in sentences:
    feats = vectorizer.transform([text])
    probs = model.predict_proba(feats)[0]
    ai_prob = float(probs[1]) * 100
    verdict = "AI-Generated" if ai_prob >= 50 else "Human Written"
    print(f"{text[:53]:<55} | {ai_prob:5.1f}% | {verdict}")

print("="*75)
