import joblib

model = joblib.load("text_model.pkl")
vectorizer = joblib.load("text_vectorizer.pkl")

textbook_samples = [
    ("NCERT Bio Ch1", "Photosynthesis is the process by which green plants and certain other organisms transform light energy into chemical energy. During photosynthesis in green plants, light energy is captured and used to convert water, carbon dioxide, and minerals into oxygen and energy-rich organic compounds."),
    ("NCERT Physics Ch3", "An electric current is a stream of charged particles, such as electrons or ions, moving through an electrical conductor or space. It is measured as the net rate of flow of electric charge through a surface or into a control volume."),
    ("History Textbook", "The French Revolution was a period of radical political and societal change in France that began with the Estates-General of 1789 and ended with the formation of the French Consulate in November 1799. Many of its ideas are considered fundamental principles of liberal democracy."),
    ("NCERT Chemistry", "Chemical reactions involve the breaking and making of bonds between atoms to produce new substances. The initial substances are known as reactants, and the resulting substances are called products."),
]

print("=" * 70)
print(f"{'Sample':<22} | {'ML AI%':<10} | {'ML Human%':<12} | {'Verdict'}")
print("=" * 70)

for title, text in textbook_samples:
    v = vectorizer.transform([text])
    p_ai = model.predict_proba(v)[0][1] * 100
    p_human = 100 - p_ai
    verdict = "Human Written" if p_human >= 50 else "AI Generated"
    print(f"{title:<22} | {p_ai:8.1f}% | {p_human:10.1f}%   | {verdict}")
print("=" * 70)
