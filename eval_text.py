import joblib
from sklearn.model_selection import cross_val_score
import train_text  # to reuse load_data

texts, labels = train_text.load_data()

vectorizer = joblib.load("text_vectorizer.pkl")
model = joblib.load("text_model.pkl")

X = vectorizer.transform(texts)

# Training accuracy (overfitting)
train_acc = model.score(X, labels)

# Cross-validation accuracy (realistic)
cv_scores = cross_val_score(model, X, labels, cv=5)

print(f"Training Accuracy (memorization): {train_acc * 100:.1f}%")
print(f"Cross-Validation Accuracy (realistic prediction on new text): {cv_scores.mean() * 100:.1f}%")
