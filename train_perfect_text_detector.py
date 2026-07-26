import os, glob, joblib, random, re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

print("="*70)
print("Building Perfect Balanced Textbook & AI Corpus...")

human_dir = os.path.join("dataset_text", "human")
ai_dir    = os.path.join("dataset_text", "ai")

all_h_files = [os.path.join(human_dir, f) for f in os.listdir(human_dir) if f.endswith('.txt')]
all_a_files = [os.path.join(ai_dir, f) for f in os.listdir(ai_dir) if f.endswith('.txt')]

txtbook_files  = [f for f in all_h_files if int(os.path.basename(f).replace('.txt','')) > 3000]
casual_h_files = [f for f in all_h_files if int(os.path.basename(f).replace('.txt','')) <= 3000]

random.seed(42)
random.shuffle(txtbook_files)
random.shuffle(casual_h_files)
random.shuffle(all_a_files)

# Select equal proportions: 600 casual human + 600 textbook human = 1200 Human
human_sample_files = casual_h_files[:600] + txtbook_files[:600]

# Select 1200 AI files
ai_sample_files = all_a_files[:1200]

ai_synthetic_passages = [
    "Photosynthesis is a fundamental biological process through which green plants, algae, and certain bacteria convert light energy into chemical energy. In this process, light energy is absorbed by chlorophyll pigments located within the chloroplasts. This energy is subsequently used to convert carbon dioxide and water into glucose and oxygen. Photosynthesis plays a crucial role in maintaining Earth's ecosystem by producing oxygen and serving as the primary source of organic matter for almost all living organisms.",
    "In today's fast-paced world, artificial intelligence plays a crucial role in modern technology. It fosters innovation across various sectors including healthcare, finance, and education. Furthermore, AI systems enable efficient data analysis and automation, allowing organizations to streamline operations and enhance decision-making processes.",
    "Furthermore, it is essential to delve into the intricate nuances of this multifaceted topic to fully understand its far-reaching implications. The integration of advanced algorithms provides a testament to human ingenuity.",
    "The cellular respiration process is vital for living organisms. It involves the breakdown of glucose molecules to release energy in the form of ATP. This metabolic pathway occurs in both aerobic and anaerobic conditions, playing a paramount role in cellular homeostasis.",
    "Understanding climate change is essential in today's rapidly changing world. Global temperatures have been steadily rising over the past century due to human activities, primarily the emission of greenhouse gases such as carbon dioxide and methane.",
    "Electric current is the flow of electric charge through a conductor. In electrical circuits, this charge is often carried by moving electrons in a wire. It can also be carried by ions in an electrolyte, or by both ions and electrons such as in an ionized gas.",
    "Quantum mechanics is a fundamental theory in physics that provides a description of the physical properties of nature at the scale of atoms and subatomic particles. It is the foundation of all quantum physics including quantum chemistry, quantum field theory, quantum technology, and quantum information science.",
    "The Industrial Revolution marked a major turning point in history; almost every aspect of daily life was influenced in some way. Average income and population began to exhibit unprecedented sustained growth.",
    "Machine learning algorithms build a model based on sample data, known as training data, in order to make predictions or decisions without being explicitly programmed to do so. Machine learning algorithms are used in a wide variety of applications, such as in medicine, email filtering, speech recognition, and computer vision."
] * 50

human_texts, ai_texts = [], []

for f in human_sample_files:
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 10:
                human_texts.append(t)
    except Exception: pass

for f in ai_sample_files:
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            t = fp.read().strip()
            if len(t.split()) >= 10:
                ai_texts.append(t)
    except Exception: pass

ai_texts.extend(ai_synthetic_passages)

n_samples = min(len(human_texts), len(ai_texts))
human_texts = human_texts[:n_samples]
ai_texts    = ai_texts[:n_samples]

texts = human_texts + ai_texts
labels = np.array([0] * len(human_texts) + [1] * len(ai_texts))

print(f"Final Dataset Balance: {len(human_texts)} Human | {len(ai_texts)} AI")

word_vectorizer = TfidfVectorizer(
    analyzer='word',
    ngram_range=(1, 2),
    max_features=4000,
    sublinear_tf=True,
    min_df=2
)

char_vectorizer = TfidfVectorizer(
    analyzer='char_wb',
    ngram_range=(3, 4),
    max_features=2500,
    sublinear_tf=True,
    min_df=2
)

union_features = FeatureUnion([
    ("word", word_vectorizer),
    ("char", char_vectorizer)
])

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.15, random_state=42, stratify=labels
)

print("Extracting TF-IDF Features...")
X_train_f = union_features.fit_transform(X_train)
X_test_f  = union_features.transform(X_test)

print("Fitting Calibrated Classifier...")
base_lr = LogisticRegression(C=2.0, max_iter=1000, random_state=42, class_weight='balanced')
calibrated_clf = CalibratedClassifierCV(estimator=base_lr, method='sigmoid', cv=3)
calibrated_clf.fit(X_train_f, y_train)

y_pred = calibrated_clf.predict(X_test_f)
acc = accuracy_score(y_test, y_pred)

print(f"\nAccuracy on Test Set: {acc * 100:.2f}%")
print(classification_report(y_test, y_pred, target_names=["Human", "AI"]))

joblib.dump(union_features, "text_vectorizer.pkl")
joblib.dump(calibrated_clf, "text_model.pkl")
print("Successfully saved calibrated model to text_vectorizer.pkl and text_model.pkl!")
