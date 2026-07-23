"""
Option B — XGBoost + LightGBM Upgraded Ensemble Classifier
Replaces Random Forest with gradient boosting models for higher accuracy.

Pipeline:
  - Word TF-IDF (1,2-grams)  — 6000 features
  - Char TF-IDF (3,5-grams)  — 3000 features
  - Stylometric Extractor     — 9 features
  - XGBoost Classifier        (gradient boosting, very high accuracy)
  - LightGBM Classifier       (fast gradient boosting, great F1 score)
  - Logistic Regression       (strong linear baseline)
  - Soft Voting Ensemble      (weighted combination of all 3)
"""

import os, glob, joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb
import lightgbm as lgb
from stylometric_transformer import StylometricExtractor

print("=" * 70)
print("  VOICE-CHECK — Option B: XGBoost + LightGBM Upgraded Ensemble")
print("=" * 70)

# ─── Load Data ──────────────────────────────────────────────────────────────
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

print(f"\nLoaded {n_human} Human samples | {n_ai} AI samples (Total: {len(texts)})")

# ─── Feature Pipeline ────────────────────────────────────────────────────────
word_tfidf = TfidfVectorizer(
    analyzer     = 'word',
    ngram_range  = (1, 2),
    max_features = 8000,
    sublinear_tf = True,
    min_df       = 2,
    strip_accents = 'unicode',
)

char_tfidf = TfidfVectorizer(
    analyzer     = 'char_wb',
    ngram_range  = (3, 5),
    max_features = 4000,
    sublinear_tf = True,
    min_df       = 3,
)

sty_pipeline = Pipeline([
    ('sty_extract', StylometricExtractor()),
    ('sty_scaler',  StandardScaler())
])

features = FeatureUnion([
    ("word", word_tfidf),
    ("char", char_tfidf),
    ("sty",  sty_pipeline)
])

# ─── Train/Test Split ────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.15, random_state=42, stratify=labels
)

print(f"\nTrain: {len(X_train)}  |  Test: {len(X_test)}")
print("\nFitting features (Word TF-IDF + Char TF-IDF + Stylometrics)...")
X_train_f = features.fit_transform(X_train)
X_test_f  = features.transform(X_test)
print(f"Feature matrix shape: {X_train_f.shape}")

# ─── Classifiers ─────────────────────────────────────────────────────────────
print("\nBuilding classifiers...")

# 1. Logistic Regression (strong linear baseline)
clf_lr = LogisticRegression(
    C=3.0,
    max_iter=1000,
    class_weight='balanced',
    random_state=42,
    solver='lbfgs'
)

# 2. XGBoost (gradient boosting — handles complex non-linear patterns)
clf_xgb = xgb.XGBClassifier(
    n_estimators      = 300,
    max_depth         = 6,
    learning_rate     = 0.1,
    subsample         = 0.8,
    colsample_bytree  = 0.8,
    eval_metric       = 'logloss',
    random_state      = 42,
    n_jobs            = -1,
    tree_method       = 'hist',   # Fast histogram-based training
)

# 3. LightGBM (fast gradient boosting — great at high-dimensional sparse data)
clf_lgb = lgb.LGBMClassifier(
    n_estimators    = 300,
    max_depth       = 6,
    learning_rate   = 0.1,
    num_leaves      = 63,
    subsample       = 0.8,
    colsample_bytree= 0.8,
    class_weight    = 'balanced',
    random_state    = 42,
    n_jobs          = -1,
    verbosity       = -1,
)

# ─── Soft Voting Ensemble (LR + XGBoost + LightGBM) ─────────────────────────
ensemble = VotingClassifier(
    estimators=[
        ('lr',  clf_lr),
        ('xgb', clf_xgb),
        ('lgb', clf_lgb),
    ],
    voting  = 'soft',
    weights = [1, 2, 2]  # XGBoost & LightGBM weighted higher
)

print("\nTraining Soft Voting Ensemble (LR + XGBoost + LightGBM)...")
print("This may take 5–15 minutes depending on dataset size...")
ensemble.fit(X_train_f, y_train)

# ─── Evaluate ────────────────────────────────────────────────────────────────
y_pred       = ensemble.predict(X_test_f)
y_pred_proba = ensemble.predict_proba(X_test_f)[:, 1]
acc          = accuracy_score(y_test, y_pred)
auc          = roc_auc_score(y_test, y_pred_proba)

print(f"\n{'='*70}")
print(f"  Test Accuracy : {acc * 100:.2f}%")
print(f"  ROC-AUC Score : {auc:.4f}")
print(f"{'='*70}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Human", "AI"]))

# ─── Save Models ─────────────────────────────────────────────────────────────
joblib.dump(features, "text_vectorizer.pkl")
joblib.dump(ensemble,  "text_model.pkl")

print("=" * 70)
print("  Saved text_vectorizer.pkl and text_model.pkl successfully!")
print(f"  Final Accuracy: {acc * 100:.2f}%  |  AUC: {auc:.4f}")
print("=" * 70)
print("Option B — XGBoost + LightGBM Ensemble COMPLETE ✅")
