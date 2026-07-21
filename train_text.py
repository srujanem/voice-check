import joblib
import os
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def load_data():
    texts = []
    labels = []
    
    # 0 = Human, 1 = AI
    human_dir = os.path.join("dataset_text", "human")
    ai_dir = os.path.join("dataset_text", "ai")
    
    # Ensure dirs exist
    os.makedirs(human_dir, exist_ok=True)
    os.makedirs(ai_dir, exist_ok=True)

    human_files = glob.glob(os.path.join(human_dir, "*.txt"))
    ai_files = glob.glob(os.path.join(ai_dir, "*.txt"))

    # Load human texts
    for f in human_files:
        with open(f, 'r', encoding='utf-8') as file:
            texts.append(file.read())
            labels.append(0)
            
    # Load AI texts
    for f in ai_files:
        with open(f, 'r', encoding='utf-8') as file:
            texts.append(file.read())
            labels.append(1)

    return texts, labels

print("Starting Text Model Training...")

texts, labels = load_data()

if not texts:
    print("Error: No text data found in dataset_text/human or dataset_text/ai.")
    print("Please add some .txt files and try again.")
    exit(1)

print(f"Loaded {len([l for l in labels if l == 0])} human texts and {len([l for l in labels if l == 1])} AI texts.")

print("Training TF-IDF model...")
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)

joblib.dump(vectorizer, "text_vectorizer.pkl")
joblib.dump(model, "text_model.pkl")

print("Training complete! Saved text_vectorizer.pkl and text_model.pkl successfully!")
