import joblib

vec = joblib.load("text_vectorizer.pkl")
model = joblib.load("text_model.pkl")

test_samples = [
    ("Real ChatGPT Essay", "In conclusion, artificial intelligence represents a transformative technology that promises to revolutionize numerous sectors. Furthermore, its ethical implications must be carefully navigated to foster a sustainable future."),
    ("Real Human Reddit Comment", "Honestly I didn't think it would work out that way lol. Was pretty surprised when they announced the changes yesterday!"),
    ("Real Human Scientific Paper", "We investigated the expression patterns of cardiac troponin in response to mechanical strain using fluorescent microscopic analysis."),
    ("Real ChatGPT Explanation", "To understand how photosynthesis works, it is important to note that plants use sunlight, water, and carbon dioxide to create oxygen and energy in the form of sugar.")
]

print("=" * 65)
print("  REAL-WORLD PREDICTION TEST (ADVANCED ENSEMBLE MODEL)")
print("=" * 65)

for label, text in test_samples:
    feat = vec.transform([text])
    prob = model.predict_proba(feat)[0]
    pred = "AI-Generated" if prob[1] >= 0.5 else "Human Written"
    conf = max(prob) * 100
    print(f"[{label}]")
    print(f"  Text   : \"{text[:80]}...\"")
    print(f"  Result : {pred} ({conf:.1f}% confidence)")
    print(f"  Scores : Human={prob[0]*100:.1f}% | AI={prob[1]*100:.1f}%\n")
