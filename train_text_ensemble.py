import os, joblib, random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

BASE = "dataset_text"
human_dirs = ["human"]
ai_dirs    = ["ai", "ai_generated"]

texts = []
labels = []

def load_dir(path, label):
    count = 0
    if not os.path.isdir(path): return 0
    for root, _, files in os.walk(path):
        for f in files:
            if not f.endswith(".txt"): continue
            try:
                with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as fp:
                    t = fp.read().strip()
                if len(t.split()) >= 8:
                    texts.append(t)
                    labels.append(label)
                    count += 1
            except Exception: pass
    return count

print("Loading dataset...")
for d in human_dirs: load_dir(os.path.join(BASE, d), 0)
for d in ai_dirs: load_dir(os.path.join(BASE, d), 1)

labels = np.array(labels)
print(f"Total: {(labels == 0).sum()} Human | {(labels == 1).sum()} AI")

# Subsample if necessary to keep training fast (max 10000 total)
combined = list(zip(texts, labels))
random.shuffle(combined)
if len(combined) > 10000:
    combined = combined[:10000]
texts, labels = zip(*combined)
texts = list(texts)
labels = np.array(labels)

X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.15, random_state=42, stratify=labels)

print("Extracting features (TF-IDF)...")
word_vec = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), max_features=30000, sublinear_tf=True, min_df=3)
char_vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), max_features=20000, sublinear_tf=True, min_df=3)

features = FeatureUnion([("word", word_vec), ("char", char_vec)])
X_train_f = features.fit_transform(X_train)
X_test_f  = features.transform(X_test)

print("Training Ensemble (Logistic + LightGBM + XGBoost)...")
clf1 = LogisticRegression(C=2.0, max_iter=2000, class_weight='balanced', solver='lbfgs')
clf2 = LGBMClassifier(n_estimators=300, learning_rate=0.1, class_weight='balanced', random_state=42)
clf3 = XGBClassifier(n_estimators=300, learning_rate=0.1, scale_pos_weight=(labels==0).sum()/(labels==1).sum(), use_label_encoder=False, eval_metric='logloss')

ensemble = VotingClassifier(
    estimators=[('lr', clf1), ('lgbm', clf2), ('xgb', clf3)],
    voting='soft'
)
ensemble.fit(X_train_f, y_train)

print("Evaluating...")
y_pred = ensemble.predict(X_test_f)
print(f"Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")

print("Saving models...")
joblib.dump(ensemble, 'text_model.pkl')
joblib.dump(features, 'text_vectorizer.pkl')
print("Done! Restart the backend to apply.")
