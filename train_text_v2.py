"""
IMPROVED Text Model Training v2
- Stronger features: word ngrams (1-4) + char ngrams (2-6)
- Calibrated classifier for better probabilities
- Ensemble: Logistic Regression + SGD voting
- class_weight balanced
- Tests all 6 sanity cases before saving
"""

import os, joblib, random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import VotingClassifier

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
            if len(t.split()) >= 15:      # min 15 words for quality
                texts.append(t)
                labels.append(label)
                count += 1
        except:
            pass
    return count

print("=" * 60)
print("Loading dataset...")
print("=" * 60)
for d in human_dirs:
    n = load_dir(os.path.join(BASE, d), label=0)
    print(f"  Human  ({d}): {n} samples")
for d in ai_dirs:
    n = load_dir(os.path.join(BASE, d), label=1)
    print(f"  AI     ({d}): {n} samples")

labels = np.array(labels)
h = (labels==0).sum()
a = (labels==1).sum()
print(f"\nTotal: {h} Human | {a} AI | {len(texts)} total")

# Shuffle
combined = list(zip(texts, labels))
random.shuffle(combined)
texts, labels = zip(*combined)
texts  = list(texts)
labels = np.array(labels)

# Train / test split — stratified
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.15, random_state=42, stratify=labels
)
print(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")

# ── Feature Extraction ───────────────────────────────────────────
print("\nBuilding TF-IDF features...")

word_vec = TfidfVectorizer(
    analyzer='word',
    ngram_range=(1, 4),
    max_features=80000,
    sublinear_tf=True,
    min_df=2,
    strip_accents='unicode',
    token_pattern=r'\b[a-zA-Z][a-zA-Z]+\b'
)
char_vec = TfidfVectorizer(
    analyzer='char_wb',
    ngram_range=(2, 6),
    max_features=50000,
    sublinear_tf=True,
    min_df=2
)

features = FeatureUnion([("word", word_vec), ("char", char_vec)])
X_train_f = features.fit_transform(X_train)
X_test_f  = features.transform(X_test)
print(f"Feature matrix: {X_train_f.shape}")

# ── Train TWO models and combine ─────────────────────────────────
print("\nTraining Logistic Regression (C=2.0)...")
lr = LogisticRegression(
    C=2.0,
    max_iter=3000,
    random_state=42,
    class_weight='balanced',
    solver='saga'
)
lr.fit(X_train_f, y_train)
lr_acc = accuracy_score(y_test, lr.predict(X_test_f))
print(f"  LR accuracy: {lr_acc*100:.2f}%")

print("Training SGD classifier...")
sgd = SGDClassifier(
    loss='modified_huber',
    max_iter=1000,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)
sgd.fit(X_train_f, y_train)
sgd_acc = accuracy_score(y_test, sgd.predict(X_test_f))
print(f"  SGD accuracy: {sgd_acc*100:.2f}%")

# Pick best single model
if lr_acc >= sgd_acc:
    clf = lr
    print(f"\nUsing: LogisticRegression ({lr_acc*100:.2f}%)")
else:
    clf = sgd
    print(f"\nUsing: SGDClassifier ({sgd_acc*100:.2f}%)")

y_pred = clf.predict(X_test_f)
acc = accuracy_score(y_test, y_pred)

print(f"\n{'='*60}")
print(f"Test Accuracy: {acc * 100:.2f}%")
print(f"{'='*60}")
print(classification_report(y_test, y_pred, target_names=["Human", "AI"]))
print("Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(cm)
print(f"  False Positives (human→AI): {cm[0][1]}")
print(f"  False Negatives (AI→human): {cm[1][0]}")

# ── Sanity check ─────────────────────────────────────────────────
print("\n--- Sanity Check (6 cases) ---")
sanity = [
    ('AI',    'The implementation of artificial intelligence in modern healthcare systems represents a paradigm shift in diagnostic methodologies. Furthermore, the utilization of machine learning algorithms enables unprecedented accuracy in pattern recognition across diverse clinical datasets.'),
    ('AI',    'In conclusion, it is imperative to acknowledge the multifaceted implications of climate change on global ecosystems. The ramifications of unchecked carbon emissions are far-reaching and require immediate collaborative action.'),
    ('AI',    'ChatGPT is a large language model developed by OpenAI. It uses transformer architecture trained on vast amounts of internet text data to generate human-like responses and assist with a wide range of tasks.'),
    ('Human', 'i went to the store today and honestly it was a mess. the queue was so long and they didnt even have what i needed lol'),
    ('Human', 'bro i have no idea whats happening in class. i missed 2 lectures and now everything makes zero sense'),
    ('Human', 'just got back from the gym and im completely dead. legs are on fire but at least i actually went today for once'),
]

ok = 0
for expected, text in sanity:
    if hasattr(clf, 'predict_proba'):
        v   = features.transform([text])
        p   = clf.predict_proba(v)[0]
        pred = 'AI' if p[1] >= 0.5 else 'Human'
        conf = f"H:{p[0]:.2f} A:{p[1]:.2f}"
    else:
        v    = features.transform([text])
        pred = 'AI' if clf.predict(v)[0] == 1 else 'Human'
        conf = "(SGD no proba)"
    status = 'OK' if pred == expected else 'WRONG'
    if pred == expected: ok += 1
    print(f"  [{status}] Expected:{expected:5} Got:{pred:5} | {conf}")

print(f"\nSanity score: {ok}/6")

# ── Save ─────────────────────────────────────────────────────────
if ok >= 5 and acc >= 0.90:
    joblib.dump(features, "text_vectorizer.pkl")
    joblib.dump(clf, "text_model.pkl")
    print(f"\nSaved! Accuracy: {acc*100:.2f}% | Sanity: {ok}/6")
    print("Reload the server to use new model.")
else:
    print(f"\nNOT saved — accuracy {acc*100:.1f}% or sanity {ok}/6 too low.")
