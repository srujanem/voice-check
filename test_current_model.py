import joblib
import sys

try:
    vectorizer = joblib.load("text_vectorizer.pkl")
    model = joblib.load("text_model.pkl")
except Exception as e:
    print(f"Error loading model: {e}")
    sys.exit(1)

human_texts = [
    "I went to the store today to buy some groceries for dinner. My mom asked me to get milk, eggs, and bread.",
    "Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy.",
    "Hey! Are we still on for tomorrow? Let me know what time works best for you."
]

ai_texts = [
    "In today's rapidly changing digital world, it is crucial to understand the implications of artificial intelligence.",
    "Overall, this multifaceted paradigm shift underscores the importance of a comprehensive strategy.",
    "Furthermore, the intricate tapestry of modern technology fosters unprecedented opportunities for growth."
]

print("--- HUMAN TEXTS ---")
for t in human_texts:
    v = vectorizer.transform([t])
    p = model.predict_proba(v)[0]
    print(f"Human Prob: {p[0]:.4f} | AI Prob: {p[1]:.4f} | Text: {t[:50]}...")

print("\n--- AI TEXTS ---")
for t in ai_texts:
    v = vectorizer.transform([t])
    p = model.predict_proba(v)[0]
    print(f"Human Prob: {p[0]:.4f} | AI Prob: {p[1]:.4f} | Text: {t[:50]}...")
