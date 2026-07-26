import os, joblib, random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

print("Loading 5000 Human vs 5000 AI dataset...")
human_dir = os.path.join("dataset_text", "human")
ai_dir    = os.path.join("dataset_text", "ai")

human_files = [os.path.join(human_dir, f) for f in os.listdir(human_dir) if f.endswith('.txt')]
ai_files    = [os.path.join(ai_dir, f) for f in os.listdir(ai_dir) if f.endswith('.txt')]

texts, labels = [], []

for f in human_files:
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 5:
                texts.append(t)
                labels.append(0)  # Human
    except Exception: pass

for f in ai_files:
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 5:
                texts.append(t)
                labels.append(1)  # AI
    except Exception: pass

labels = np.array(labels)
print(f"Dataset Balanced: {(labels==0).sum()} Human | {(labels==1).sum()} AI")

word_vec = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), max_features=4000, sublinear_tf=True, min_df=2)
char_vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 4), max_features=2500, sublinear_tf=True, min_df=2)

features = FeatureUnion([("word", word_vec), ("char", char_vec)])

X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.15, random_state=42, stratify=labels)

X_train_f = features.fit_transform(X_train)
X_test_f  = features.transform(X_test)

clf = LogisticRegression(C=2.0, max_iter=1000, random_state=42)
clf.fit(X_train_f, y_train)

y_pred = clf.predict(X_test_f)
acc = accuracy_score(y_test, y_pred)

print(f"\nModel Accuracy: {acc * 100:.2f}%")
print(classification_report(y_test, y_pred, target_names=["Human", "AI"]))

joblib.dump(features, "text_vectorizer.pkl")
joblib.dump(clf, "text_model.pkl")
print("Saved text_vectorizer.pkl and text_model.pkl successfully!")
