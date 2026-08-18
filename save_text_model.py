"""
Quick save: retrain and save text model (fixed unicode issue)
"""
import sys, os, joblib, random
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

BASE = "dataset_text"
texts, labels = [], []

def load_dir(dirpath, label):
    if not os.path.exists(dirpath): return 0
    count = 0
    for fname in os.listdir(dirpath):
        fpath = os.path.join(dirpath, fname)
        if not os.path.isfile(fpath): continue
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                t = fp.read().strip()
            if len(t.split()) >= 15:
                texts.append(t)
                labels.append(label)
                count += 1
        except: pass
    return count

for d in ["human"]:
    n = load_dir(os.path.join(BASE, d), 0)
    print(f"Human ({d}): {n}")
for d in ["ai", "ai_generated"]:
    n = load_dir(os.path.join(BASE, d), 1)
    print(f"AI ({d}): {n}")

labels = np.array(labels)
print(f"Total: {(labels==0).sum()} Human | {(labels==1).sum()} AI")

combined = list(zip(texts, labels))
random.shuffle(combined)
texts, labels = zip(*combined)
texts = list(texts)
labels = np.array(labels)

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.15, random_state=42, stratify=labels)

word_vec = TfidfVectorizer(
    analyzer='word', ngram_range=(1, 4), max_features=80000,
    sublinear_tf=True, min_df=2, strip_accents='unicode',
    token_pattern=r'\b[a-zA-Z][a-zA-Z]+\b')
char_vec = TfidfVectorizer(
    analyzer='char_wb', ngram_range=(2, 6), max_features=50000,
    sublinear_tf=True, min_df=2)

features = FeatureUnion([("word", word_vec), ("char", char_vec)])
print("Building features...")
X_train_f = features.fit_transform(X_train)
X_test_f  = features.transform(X_test)

print("Training SGD...")
clf = SGDClassifier(loss='modified_huber', max_iter=1000, random_state=42,
                    class_weight='balanced', n_jobs=-1)
clf.fit(X_train_f, y_train)
acc = accuracy_score(y_test, clf.predict(X_test_f))
print(f"Accuracy: {acc*100:.2f}%")

# Sanity
sanity = [
    ('AI',    'Artificial intelligence has revolutionized numerous industries over the past decade. From healthcare to finance, machine learning models are increasingly deployed to automate complex tasks and improve decision-making processes.'),
    ('AI',    'Great question! There are several key factors to consider. First and foremost, it is important to understand the underlying mechanisms. Additionally, we must take into account the broader socioeconomic context in which these developments occur.'),
    ('Human', 'i went to the store today and honestly it was a mess. the queue was so long and they didnt even have what i needed lol'),
    ('Human', 'bro i have no idea whats happening in class. i missed 2 lectures and now everything makes zero sense'),
]
ok = 0
for expected, text in sanity:
    v = features.transform([text])
    p = clf.predict_proba(v)[0]
    pred = 'AI' if p[1] >= 0.5 else 'Human'
    correct = pred == expected
    if correct: ok += 1
    s = 'OK' if correct else 'WRONG'
    print(f"  [{s}] Expected:{expected} Got:{pred} H:{p[0]:.2f} A:{p[1]:.2f}")

print(f"Sanity: {ok}/4")

if acc >= 0.95 and ok >= 3:
    joblib.dump(features, "text_vectorizer.pkl")
    joblib.dump(clf, "text_model.pkl")
    print(f"SAVED! text_model.pkl + text_vectorizer.pkl ({acc*100:.2f}%)")
else:
    print("NOT saved - check results above")
