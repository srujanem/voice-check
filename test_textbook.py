import joblib
from backend.services.perplexity_engine import perplexity_engine

model = joblib.load("text_model.pkl")
vectorizer = joblib.load("text_vectorizer.pkl")

textbook_samples = [
    ("NCERT Bio Ch1", "Photosynthesis is the process by which green plants and certain other organisms transform light energy into chemical energy. During photosynthesis in green plants, light energy is captured and used to convert water, carbon dioxide, and minerals into oxygen and energy-rich organic compounds."),
    ("NCERT Physics Ch3", "An electric current is a stream of charged particles, such as electrons or ions, moving through an electrical conductor or space. It is measured as the net rate of flow of electric charge through a surface or into a control volume."),
    ("History Textbook", "The French Revolution was a period of radical political and societal change in France that began with the Estates-General of 1789 and ended with the formation of the French Consulate in November 1799. Many of its ideas are considered fundamental principles of liberal democracy."),
    ("NCERT Chemistry", "Chemical reactions involve the breaking and making of bonds between atoms to produce new substances. The initial substances are known as reactants, and the resulting substances are called products."),
]

print("=" * 80)
print(f"{'Sample':<20} | {'ML AI%':<10} | {'PPL':<6} | {'Burstiness':<10} | {'Current Final AI%'}")
print("=" * 80)

for title, text in textbook_samples:
    v = vectorizer.transform([text])
    p_ml = model.predict_proba(v)[0][1] * 100
    
    ppl_res = perplexity_engine.analyze(text)
    ppl = ppl_res["perplexity"]
    burst = ppl_res["burstiness"]
    
    if ppl < 30 and burst < 4.0:
        ppl_mod = 0.12
    elif ppl < 40:
        ppl_mod = 0.06
    elif ppl > 75:
        ppl_mod = -0.12
    elif ppl > 60:
        ppl_mod = -0.06
    else:
        ppl_mod = 0.0
        
    final_ai = min(100.0, max(0.0, p_ml + (ppl_mod * 100)))
    print(f"{title:<20} | {p_ml:8.1f}% | {ppl:<6.1f} | {burst:<10.1f} | {final_ai:15.1f}%")
print("=" * 80)
