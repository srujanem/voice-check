import joblib

vec = joblib.load("text_vectorizer.pkl")
model = joblib.load("text_model.pkl")

test_samples = [
    ("Human (casual chat)", "Hey man, sorry I couldn't make it to the party last night! Got stuck working late on my assignment. Let's hang out this weekend instead."),
    ("AI (ChatGPT style)", "Certainly! Here is a comprehensive overview of quantum computing. Quantum computing is a rapidly emerging technology that harnesses the laws of quantum mechanics to solve complex problems."),
    ("Human (story)", "The old wooden door creaked open as Sarah pushed it with her shoulder. Dust swirled in the thin beam of sunlight cutting through the darkness."),
    ("AI (formal essay)", "Furthermore, it is essential to consider the multifaceted nature of environmental sustainability. In conclusion, adopting green energy policies is imperative.")
]

print("=" * 65)
print("  REAL-WORLD PREDICTION TEST (HC3 MODEL)")
print("=" * 65)

for label, text in test_samples:
    feat = vec.transform([text])
    prob = model.predict_proba(feat)[0]
    pred = "AI-Generated" if prob[1] >= 0.5 else "Human Written"
    conf = max(prob) * 100
    print(f"[{label}]")
    print(f"  Result : {pred} ({conf:.1f}% confidence)")
    print(f"  Scores : Human={prob[0]*100:.1f}% | AI={prob[1]*100:.1f}%\n")
