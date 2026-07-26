import os, glob, joblib, random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

print("="*75)
print("Training Clean Real-World AI vs Human Text Classifier...")

human_dir = os.path.join("dataset_text", "human")
ai_dir    = os.path.join("dataset_text", "ai")

# Load real HC3 Human files (files 1 to 5000)
human_files = [os.path.join(human_dir, f) for f in os.listdir(human_dir) if f.endswith('.txt') and f.replace('.txt','').isdigit() and int(f.replace('.txt','')) <= 5000]

# Load real HC3 AI files (files 1 to 5000)
ai_files = [os.path.join(ai_dir, f) for f in os.listdir(ai_dir) if f.endswith('.txt') and f.replace('.txt','').isdigit() and int(f.replace('.txt','')) <= 5000]

random.seed(42)
random.shuffle(human_files)
random.shuffle(ai_files)

texts, labels = [], []

for f in human_files:
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 8:
                texts.append(t)
                labels.append(0)  # Human
    except Exception: pass

for f in ai_files:
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 8:
                texts.append(t)
                labels.append(1)  # AI
    except Exception: pass

# Add AI stylistic phrase openers ONLY (no science subject terms)
ai_extra_prompts = [
    "In today's fast-paced world, artificial intelligence plays a crucial role in modern technology. It fosters innovation across various sectors including healthcare, finance, and education.",
    "Furthermore, it is essential to delve into the intricate nuances of this multifaceted topic to fully understand its far-reaching implications and testament to innovation.",
    "In conclusion, machine learning provides significant benefits by streamlining complex data processing and enhancing decision-making capabilities across industries.",
    "Artificial intelligence is transforming the world by enabling automated reasoning, pattern recognition, and predictive analytics at unprecedented scale.",
    "This article explores the key factors influencing economic growth, technological adoption, and market efficiency in modern global economies."
] * 40

for t in ai_extra_prompts:
    texts.append(t)
    labels.append(1)

labels = np.array(labels)
n_h = (labels == 0).sum()
n_a = (labels == 1).sum()
print(f"Clean Real-World Dataset: {n_h} Human | {n_a} AI (Total: {len(labels)})")

word_vec = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), max_features=15000, sublinear_tf=True, min_df=2)
features = word_vec

X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.15, random_state=42, stratify=labels)

X_train_f = features.fit_transform(X_train)
X_test_f  = features.transform(X_test)

clf = LogisticRegression(C=2.5, max_iter=1000, random_state=42, class_weight='balanced')
clf.fit(X_train_f, y_train)

y_pred = clf.predict(X_test_f)
acc = accuracy_score(y_test, y_pred)

print(f"\nModel Accuracy on Test Set: {acc * 100:.2f}%")
print(classification_report(y_test, y_pred, target_names=["Human", "AI"]))

joblib.dump(features, "text_vectorizer.pkl")
joblib.dump(clf, "text_model.pkl")
print("Saved clean real-world text_vectorizer.pkl and text_model.pkl successfully!")
