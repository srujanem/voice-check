import os, glob, random, joblib
import pdfplumber
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

print("=" * 70)
print("  VOICE-CHECK — Textbook-Aware Classifier Training")
print("=" * 70)

pdf_dir = r'C:\Users\sruja\.gemini\antigravity\brain\656ffd67-2c5d-4c4e-a46e-fd5792eed8db\.user_uploaded'
pdf_files = [f for f in glob.glob(os.path.join(pdf_dir, '*.pdf')) if os.path.getsize(f) > 1000]

print(f"Reading {len(pdf_files)} textbook PDFs...")
textbook_chunks = []

for pdf_path in pdf_files:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:10]: # First 10 pages per PDF for high speed
                txt = page.extract_text()
                if txt:
                    words = txt.split()
                    for i in range(0, len(words), 50):
                        c = " ".join(words[i:i+50])
                        if len(c.split()) >= 15:
                            textbook_chunks.append(c)
    except Exception as e:
        pass

print(f"Extracted {len(textbook_chunks)} formal academic textbook passages.")

human_files = glob.glob(os.path.join("dataset_text", "human", "*.txt"))
ai_files    = glob.glob(os.path.join("dataset_text", "ai", "*.txt"))

random.seed(42)
random.shuffle(human_files)
random.shuffle(ai_files)

texts, labels = [], []

# Add textbook passages as Human (Label 0)
for c in textbook_chunks[:1500]:
    texts.append(c)
    labels.append(0)

# Add regular Human answers
for f in human_files[:1500]:
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 10:
                texts.append(t)
                labels.append(0)
    except Exception: pass

# Add AI answers
for f in ai_files[:len(texts)]:
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 10:
                texts.append(t)
                labels.append(1)
    except Exception: pass

labels = np.array(labels)
print(f"Dataset: {(labels==0).sum()} Human (Textbook + Casual) | {(labels==1).sum()} AI (Total: {len(texts)})")

word_tfidf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), max_features=5000, sublinear_tf=True, min_df=2)
char_tfidf = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 4), max_features=3000, sublinear_tf=True, min_df=2)

from sklearn.pipeline import FeatureUnion
features = FeatureUnion([("word", word_tfidf), ("char", char_tfidf)])

X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.15, random_state=42, stratify=labels)

X_train_f = features.fit_transform(X_train)
X_test_f  = features.transform(X_test)

clf = LogisticRegression(C=3.0, max_iter=1000, random_state=42)
clf.fit(X_train_f, y_train)

y_pred = clf.predict(X_test_f)
acc    = accuracy_score(y_test, y_pred)

print(f"\nTest Accuracy: {acc * 100:.2f}%")
print(classification_report(y_test, y_pred, target_names=["Human", "AI"]))

joblib.dump(features, "text_vectorizer.pkl")
joblib.dump(clf, "text_model.pkl")
print("Saved text_vectorizer.pkl and text_model.pkl successfully!")
