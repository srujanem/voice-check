"""
FIXED Text Model Training Script
- Loads from dataset_text/human (label=0) AND dataset_text/ai + ai_generated (label=1)
- Uses class_weight='balanced' to handle any imbalance
- Stronger TF-IDF features (word + char n-grams)
- Tests on real examples before saving
- Saves to text_model.pkl and text_vectorizer.pkl (root dir, where ml_engine expects them)
"""

import os, joblib, random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# ── 1. Load ALL text data ────────────────────────────────────────────────────
BASE = "dataset_text"
human_dirs = ["human"]
ai_dirs    = ["ai", "ai_generated"]

texts, labels = [], []

def load_dir(dirpath, label):
    count = 0
    if not os.path.exists(dirpath):
        print(f"  [SKIP] {dirpath} not found")
        return 0
    for fname in os.listdir(dirpath):
        fpath = os.path.join(dirpath, fname)
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                t = fp.read().strip()
            if len(t.split()) >= 10:   # min 10 words
                texts.append(t)
                labels.append(label)
                count += 1
        except Exception:
            pass
    return count

print("=" * 55)
print("Loading dataset...")
print("=" * 55)
for d in human_dirs:
    n = load_dir(os.path.join(BASE, d), label=0)
    print(f"  Human  ({d}): {n} samples")

for d in ai_dirs:
    n = load_dir(os.path.join(BASE, d), label=1)
    print(f"  AI     ({d}): {n} samples")

labels = np.array(labels)
human_count = (labels == 0).sum()
ai_count    = (labels == 1).sum()
print(f"\nTotal: {human_count} Human | {ai_count} AI | {len(texts)} total")

if human_count < 10 or ai_count < 10:
    print("ERROR: Not enough data. Need at least 10 samples per class.")
    exit(1)

# ── 2. Shuffle ───────────────────────────────────────────────────────────────
combined = list(zip(texts, labels))
random.shuffle(combined)
texts, labels = zip(*combined)
texts = list(texts)
labels = np.array(labels)

# ── 3. Train / Test Split ────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.15, random_state=42, stratify=labels
)
print(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")

# ── 4. Feature Extraction (TF-IDF word + char) ───────────────────────────────
print("\nBuilding TF-IDF features...")
word_vec = TfidfVectorizer(
    analyzer='word',
    ngram_range=(1, 3),      # up to trigrams
    max_features=50000,
    sublinear_tf=True,
    min_df=2,
    strip_accents='unicode',
    token_pattern=r'\b[a-zA-Z][a-zA-Z]+\b'
)
char_vec = TfidfVectorizer(
    analyzer='char_wb',
    ngram_range=(3, 5),
    max_features=30000,
    sublinear_tf=True,
    min_df=2
)

features = FeatureUnion([("word", word_vec), ("char", char_vec)])
X_train_f = features.fit_transform(X_train)
X_test_f  = features.transform(X_test)
print(f"Feature matrix: {X_train_f.shape}")

# ── 5. Train Logistic Regression ─────────────────────────────────────────────
print("\nTraining Logistic Regression...")
clf = LogisticRegression(
    C=1.5,
    max_iter=2000,
    random_state=42,
    class_weight='balanced',   # handles imbalance automatically
    solver='lbfgs',
    n_jobs=-1
)
clf.fit(X_train_f, y_train)

# ── 6. Evaluate ──────────────────────────────────────────────────────────────
y_pred = clf.predict(X_test_f)
acc = accuracy_score(y_test, y_pred)

print(f"\n{'='*55}")
print(f"Test Accuracy: {acc * 100:.2f}%")
print(f"{'='*55}")
print(classification_report(y_test, y_pred, target_names=["Human", "AI"]))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ── 7. Sanity check on real examples ────────────────────────────────────────
print("\n--- Sanity Check ---")
test_cases = [
    ("AI", "The implementation of artificial intelligence in modern healthcare systems represents a paradigm shift in diagnostic methodologies. Furthermore, the utilization of machine learning algorithms enables unprecedented accuracy in pattern recognition across diverse clinical datasets."),
    ("AI", "In this essay, I will delve into the multifaceted dimensions of climate change and its far-reaching implications on global ecosystems. It is important to note that the ramifications of greenhouse gas emissions extend beyond mere temperature fluctuations."),
    ("Human", "I went to the store today and bought some groceries. It was pretty hot outside but the walk was nice. My dog came with me which made it way more fun than usual."),
    ("Human", "honestly i have no idea why my code isn't working. i've been staring at it for 2 hours and it just keeps throwing the same error. maybe i'll just restart my computer and see what happens lol"),
]
for expected, text in test_cases:
    vec = features.transform([text])
    probs = clf.predict_proba(vec)[0]
    pred = "AI" if probs[1] >= 0.5 else "Human"
    status = "OK" if pred == expected else "WRONG"
    print(f"  [{status}] Expected:{expected} Got:{pred} | H:{probs[0]:.2f} A:{probs[1]:.2f}")

# ── 8. Save models ───────────────────────────────────────────────────────────
if acc >= 0.70:
    joblib.dump(features, "text_vectorizer.pkl")
    joblib.dump(clf, "text_model.pkl")
    print(f"\nSaved text_vectorizer.pkl and text_model.pkl (accuracy: {acc*100:.1f}%)")
    print("Restart your backend to load the new model.")
else:
    print(f"\nAccuracy too low ({acc*100:.1f}%). Models NOT saved. Check your dataset.")
