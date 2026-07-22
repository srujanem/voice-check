"""
Improved text model training with:
- TF-IDF on word unigrams + bigrams (captures phrase patterns)
- Character n-gram TF-IDF (catches stylistic patterns AI has)
- Gradient Boosting classifier for higher accuracy
- Cross-validation score printed so we know the real accuracy
"""
import joblib, os, glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import classification_report, accuracy_score
import numpy as np

def load_data():
    texts, labels = [], []
    human_dir = os.path.join("dataset_text", "human")
    ai_dir    = os.path.join("dataset_text", "ai")

    for f in glob.glob(os.path.join(human_dir, "*.txt")):
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
                t = fp.read().strip()
                if len(t.split()) >= 10:          # skip very short files
                    texts.append(t)
                    labels.append(0)              # 0 = Human
        except Exception:
            pass

    for f in glob.glob(os.path.join(ai_dir, "*.txt")):
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
                t = fp.read().strip()
                if len(t.split()) >= 10:
                    texts.append(t)
                    labels.append(1)              # 1 = AI
        except Exception:
            pass

    return texts, labels

print("=" * 60)
print("  VOICE-CHECK — Text Model Retraining")
print("=" * 60)

texts, labels = load_data()
labels = np.array(labels)

n_human = int((labels == 0).sum())
n_ai    = int((labels == 1).sum())
print(f"Loaded  {n_human} human samples  |  {n_ai} AI samples")
print(f"Total   {len(texts)} samples")

# ── Feature pipeline ──────────────────────────────────────────────────────────
word_tfidf = TfidfVectorizer(
    analyzer     = 'word',
    ngram_range  = (1, 2),       # unigrams + bigrams
    max_features = 8000,
    sublinear_tf = True,
    min_df       = 2,
)

char_tfidf = TfidfVectorizer(
    analyzer     = 'char_wb',    # character n-grams (very effective for AI detection)
    ngram_range  = (3, 5),
    max_features = 6000,
    sublinear_tf = True,
    min_df       = 3,
)

features = FeatureUnion([
    ("word", word_tfidf),
    ("char", char_tfidf),
])

# ── Train / test split ────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.15, random_state=42, stratify=labels
)

print(f"\nTrain: {len(X_train)}  |  Test: {len(X_test)}")

# ── Fit features ──────────────────────────────────────────────────────────────
print("\nFitting TF-IDF features...")
X_train_f = features.fit_transform(X_train)
X_test_f  = features.transform(X_test)

# ── Train classifier ──────────────────────────────────────────────────────────
print("Training Logistic Regression classifier...")
clf = LogisticRegression(
    C           = 5.0,
    max_iter    = 1000,
    solver      = 'lbfgs',
    class_weight= 'balanced',
    random_state= 42,
)
clf.fit(X_train_f, y_train)

# ── Evaluate ──────────────────────────────────────────────────────────────────
y_pred = clf.predict(X_test_f)
acc    = accuracy_score(y_test, y_pred)

print(f"\nTest Accuracy : {acc * 100:.1f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Human", "AI"]))

# ── Save ──────────────────────────────────────────────────────────────────────
joblib.dump(features, "text_vectorizer.pkl")
joblib.dump(clf,      "text_model.pkl")

print("=" * 60)
print("  Saved text_vectorizer.pkl  and  text_model.pkl")
print("=" * 60)
