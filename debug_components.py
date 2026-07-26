import joblib, torch, numpy as np
from stylometric_transformer import StylometricExtractor
from backend.services.perplexity_engine import perplexity_engine
from backend.services.distilbert_engine import distilbert_engine

# Load ML ensemble
model = joblib.load("text_model.pkl")
vectorizer = joblib.load("text_vectorizer.pkl")

tests = [
    ("AI", "Understanding climate change is essential in today's rapidly changing world. Climate change and its effects on ecosystems touches on fundamental questions that affect both individuals and society as a whole. From an environmental science perspective, several key mechanisms are at work. Researchers have identified multiple contributing factors, each of which plays a distinct role. Key areas of focus include: 1. Understanding foundational principles 2. Analyzing empirical evidence 3. Evaluating policy implications. In summary, climate change demands careful, evidence-based inquiry."),
    ("AI", "Artificial intelligence represents a paradigm shift in how we approach complex problem-solving. The underlying architecture is designed to be highly scalable and robust. By utilizing distributed networks, it minimizes latency and maximizes throughput. Furthermore, it is important to consider the ethical implications inherent in such systems. Regular audits and transparent methodologies are highly recommended. Ultimately, fostering a collaborative ecosystem will be key to unlocking the full potential of AI."),
    ("AI", "Photosynthesis is a fundamental biological process whereby plants convert sunlight into chemical energy. This process occurs primarily in the chloroplasts, where chlorophyll absorbs light in the red and blue wavelengths. The light-dependent reactions produce ATP and NADPH, which are subsequently used in the Calvin cycle to fix atmospheric carbon dioxide into glucose. Understanding photosynthesis has significant implications for agriculture, biofuel development, and our understanding of the global carbon cycle."),
    ("Human", "Mahatma Gandhi launched the Non-Cooperation Movement in 1920 to protest against the Rowlatt Act and the Jallianwala Bagh massacre. Thousands of students left government-run schools and colleges, while lawyers gave up their practice in courts. People burnt foreign-made cloth and adopted khadi. The movement gained tremendous momentum across the country."),
    ("Human", "Growing up in a coastal village meant our lives revolved around the ocean tides. Every afternoon when the fishing boats returned to the shore, the beach transformed into a bustling marketplace. Men unloaded nets heavy with pomfret, mackerel, and prawns, while women sorted the catch into wicker baskets."),
    ("Human", "Mitochondria are often described as the powerhouse of the cell because they generate most of the chemical energy needed to power cellular biochemical reactions. Energy produced by mitochondria is stored in a small molecule called adenosine triphosphate. The mitochondria of cells that require large amounts of energy, such as muscle cells, are more numerous and have more cristae than those in less active cells."),
]

print("=" * 80)
print(f"{'Target':<8} | {'XGBoost ML AI%':<15} | {'Perplexity (PPL/Std)':<22} | {'DistilBERT AI%':<15} | {'Fused AI%'}")
print("=" * 80)

for label, text in tests:
    # 1. XGBoost ML
    v = vectorizer.transform([text])
    p_xgb = model.predict_proba(v)[0][1] * 100

    # 2. Perplexity Engine
    ppl_res = perplexity_engine.analyze(text)
    ppl = ppl_res["perplexity"]
    burstiness = ppl_res["burstiness"]
    if ppl < 40: ppl_score = 0.95
    elif ppl < 55: ppl_score = 0.80
    elif ppl > 80: ppl_score = 0.10
    elif ppl > 65: ppl_score = 0.25
    else: ppl_score = 0.50

    # 3. DistilBERT
    bert_res = distilbert_engine.predict(text)
    p_bert = bert_res["prob_ai"] * 100 if bert_res else 0.0

    # Fused
    fused = (0.40 * (p_xgb/100)) + (0.30 * ppl_score) + (0.30 * (p_bert/100))

    print(f"{label:<8} | {p_xgb:13.1f}% | PPL={ppl:<5.1f} B={burstiness:<5.1f} ({ppl_score*100:.0f}%) | {p_bert:13.1f}% | {fused*100:8.1f}%")
print("=" * 80)
