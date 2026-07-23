import os, glob, joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from stylometric_transformer import StylometricExtractor

print("=" * 65)
print("  VOICE-CHECK — Calibrated Ensemble Retraining")
print("=" * 65)

# Load data
human_dir = os.path.join("dataset_text", "human")
ai_dir    = os.path.join("dataset_text", "ai")

texts, labels = [], []

for f in glob.glob(os.path.join(human_dir, "*.txt")):
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 10:
                texts.append(t)
                labels.append(0)  # 0 = Human
    except Exception:
        pass

for f in glob.glob(os.path.join(ai_dir, "*.txt")):
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 10:
                texts.append(t)
                labels.append(1)  # 1 = AI
    except Exception:
        pass

labels = np.array(labels)
n_human = int((labels == 0).sum())
n_ai    = int((labels == 1).sum())

print(f"Loaded {n_human} Human samples | {n_ai} AI samples (Total: {len(texts)})")

# Feature Pipeline
word_tfidf = TfidfVectorizer(
    analyzer     = 'word',
    ngram_range  = (1, 2),
    max_features = 6000,
    sublinear_tf = True,
    min_df       = 2,
)

char_tfidf = TfidfVectorizer(
    analyzer     = 'char_wb',
    ngram_range  = (3, 5),
    max_features = 3000,
    sublinear_tf = True,
    min_df       = 3,
)

sty_pipeline = Pipeline([
    ('sty_extract', StylometricExtractor()),
    ('sty_scaler', StandardScaler())
])

features = FeatureUnion([
    ("word", word_tfidf),
    ("char", char_tfidf),
    ("sty", sty_pipeline)
])

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.15, random_state=42, stratify=labels
)

print(f"\nTrain: {len(X_train)}  |  Test: {len(X_test)}")
print("\nFitting TF-IDF + Stylometric & Burstiness features...")
X_train_f = features.fit_transform(X_train)
X_test_f  = features.transform(X_test)

# Classifiers for Voting Ensemble
clf_lr = LogisticRegression(C=3.0, max_iter=1000, class_weight='balanced', random_state=42)
clf_rf = RandomForestClassifier(n_estimators=100, max_depth=15, class_weight='balanced', random_state=42, n_jobs=-1)

ensemble = VotingClassifier(
    estimators=[
        ('lr', clf_lr),
        ('rf', clf_rf)
    ],
    voting='soft',
    weights=[2, 1]  # Weight LogisticRegression slightly higher for smooth confidence calibration
)

print("Training Calibrated Soft Voting Ensemble Classifier...")
ensemble.fit(X_train_f, y_train)

y_pred = ensemble.predict(X_test_f)
acc = accuracy_score(y_test, y_pred)

print(f"\nTest Accuracy: {acc * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Human", "AI"]))

joblib.dump(features, "text_vectorizer.pkl")
joblib.dump(ensemble, "text_model.pkl")

print("=" * 65)
print("  Saved text_vectorizer.pkl and text_model.pkl successfully!")
print("=" * 65)
