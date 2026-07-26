import joblib
import sys
import numpy as np

vectorizer = joblib.load("text_vectorizer.pkl")
model = joblib.load("text_model.pkl")

import PyPDF2

pdf_path = r"C:\Users\sruja\.gemini\antigravity\brain\656ffd67-2c5d-4c4e-a46e-fd5792eed8db\.user_uploaded\media__1784800001060.pdf"
text = ""
with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    for i in range(min(2, len(reader.pages))):
        text += reader.pages[i].extract_text() + "\n"


v = vectorizer.transform([text])
p = model.predict_proba(v)[0]
print(f"Prediction -> Human: {p[0]:.4f} | AI: {p[1]:.4f}")

# Get feature names
feature_names = vectorizer.get_feature_names_out()
# Get non-zero elements
non_zero = v.nonzero()[1]

print("Top contributing features for this text:")
contributions = []
for idx in non_zero:
    feat = feature_names[idx]
    weight = model.coef_[0][idx]
    val = v[0, idx]
    contributions.append((feat, weight * val))

contributions.sort(key=lambda x: x[1], reverse=True)
print("\n--- Features pushing towards AI (> 0) ---")
for feat, score in contributions[:15]:
    if score > 0: print(f"{feat}: {score:.4f}")

print("\n--- Features pushing towards Human (< 0) ---")
for feat, score in contributions[-15:]:
    if score < 0: print(f"{feat}: {score:.4f}")
