import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import os

# Dummy dataset for demonstration
texts = [
    # AI generated
    "In conclusion, it is important to note that the proliferation of artificial intelligence has significantly impacted modern society.",
    "Furthermore, the integration of synergistic methodologies allows for unprecedented scalability.",
    "As an AI language model, I do not have personal opinions, but I can provide an objective analysis.",
    "Delving into the realm of possibilities, one must consider the multifaceted approach required.",
    "Ultimately, the transformative power of this technology cannot be understated in today's fast-paced world.",
    "It is crucial to recognize that the aforementioned factors contribute to a comprehensive understanding of the paradigm.",
    # Human written
    "I really didn't expect the movie to end like that, it was super weird.",
    "Hey can you grab some milk on your way home?",
    "The new Zelda game is actually incredible, I've played it for 50 hours already.",
    "Bro I swear I left my keys right here on the counter.",
    "Just finished reading the book and tbh it wasn't as good as people said it was.",
    "im so tired today i think im just gonna sleep early."
]
labels = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]  # 1 = AI, 0 = Human

print("Training basic TF-IDF model for Text Detection...")

vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)

joblib.dump(vectorizer, "text_vectorizer.pkl")
joblib.dump(model, "text_model.pkl")

print("Saved text_vectorizer.pkl and text_model.pkl successfully!")
