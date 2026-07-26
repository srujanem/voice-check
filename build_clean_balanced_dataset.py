import os, glob, joblib, random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

print("Building Clean Balanced Training Corpus...")

human_dir = os.path.join("dataset_text", "human")
ai_dir    = os.path.join("dataset_text", "ai")

all_h = [os.path.join(human_dir, f) for f in os.listdir(human_dir) if f.endswith('.txt')]
all_a = [os.path.join(ai_dir, f) for f in os.listdir(ai_dir) if f.endswith('.txt')]

# Separate textbook files (> 3000) and casual files (<= 3000)
txtbook_files  = [f for f in all_h if int(os.path.basename(f).replace('.txt','')) > 3000]
casual_h_files = [f for f in all_h if int(os.path.basename(f).replace('.txt','')) <= 3000]

random.seed(42)
random.shuffle(txtbook_files)
random.shuffle(casual_h_files)
random.shuffle(all_a)

# Select 1,000 casual human + 300 textbook human = 1,300 Human
selected_h = casual_h_files[:1000] + txtbook_files[:300]
selected_a = all_a[:1300]

human_texts, ai_texts = [], []

for f in selected_h:
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 10:
                human_texts.append(t)
    except Exception: pass

for f in selected_a:
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 10:
                ai_texts.append(t)
    except Exception: pass

n = min(len(human_texts), len(ai_texts))
human_texts = human_texts[:n]
ai_texts    = ai_texts[:n]

texts  = human_texts + ai_texts
labels = np.array([0] * n + [1] * n)  # 0 = Human, 1 = AI

print(f"Dataset Balanced: {n} Human ({len(txtbook_files[:300])} Textbooks + {len(casual_h_files[:1000])} Casual) | {n} AI")

word_vec = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), max_features=5000, sublinear_tf=True, min_df=2)
char_vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 4), max_features=3000, sublinear_tf=True, min_df=2)

features = FeatureUnion([("word", word_vec), ("char", char_vec)])

X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.15, random_state=42, stratify=labels)

X_train_f = features.fit_transform(X_train)
X_test_f  = features.transform(X_test)

lr = LogisticRegression(C=2.0, max_iter=1000, random_state=42)
clf = CalibratedClassifierCV(estimator=lr, method='sigmoid', cv=3)
clf.fit(X_train_f, y_train)

y_pred = clf.predict(X_test_f)
print(f"Test Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print(classification_report(y_test, y_pred, target_names=["Human", "AI"]))

joblib.dump(features, "text_vectorizer.pkl")
joblib.dump(clf, "text_model.pkl")
print("Saved text_vectorizer.pkl and text_model.pkl successfully!")
