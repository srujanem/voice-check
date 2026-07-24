import os, joblib, random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

print("Loading textbook + casual dataset...")
human_dir = os.path.join("dataset_text", "human")
ai_dir    = os.path.join("dataset_text", "ai")

all_h = os.listdir(human_dir)

txtbook_files = [os.path.join(human_dir, f) for f in all_h if f.endswith('.txt') and int(f.replace('.txt','')) > 3000]
casual_files  = [os.path.join(human_dir, f) for f in all_h if f.endswith('.txt') and int(f.replace('.txt','')) <= 3000][:600]

random.seed(42)
random.shuffle(txtbook_files)
txtbook_files = txtbook_files[:600]

human_files = txtbook_files + casual_files

all_a = os.listdir(ai_dir)
ai_files = [os.path.join(ai_dir, f) for f in all_a if f.endswith('.txt')][:len(human_files)]

random.seed(42)
random.shuffle(human_files)
random.shuffle(ai_files)

texts, labels = [], []

for f in human_files:
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 10:
                texts.append(t)
                labels.append(0)  # Human
    except Exception: pass

for f in ai_files:
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 10:
                texts.append(t)
                labels.append(1)  # AI
    except Exception: pass

labels = np.array(labels)
print(f"Dataset: {(labels==0).sum()} Human ({len(txtbook_files)} Textbooks + {len(casual_files)} Casual) | {(labels==1).sum()} AI")

word_tfidf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), max_features=7000, sublinear_tf=True, min_df=2)
char_tfidf = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), max_features=4000, sublinear_tf=True, min_df=2)

features = FeatureUnion([("word", word_tfidf), ("char", char_tfidf)])

X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.15, random_state=42, stratify=labels)

X_train_f = features.fit_transform(X_train)
X_test_f  = features.transform(X_test)

clf = LogisticRegression(C=5.0, max_iter=1000, random_state=42)
clf.fit(X_train_f, y_train)

y_pred = clf.predict(X_test_f)
acc = accuracy_score(y_test, y_pred)

print(f"Accuracy: {acc * 100:.2f}%")
print(classification_report(y_test, y_pred, target_names=["Human", "AI"]))

joblib.dump(features, "text_vectorizer.pkl")
joblib.dump(clf, "text_model.pkl")
print("Saved text_vectorizer.pkl and text_model.pkl successfully!")
