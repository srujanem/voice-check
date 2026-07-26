import joblib

model = joblib.load("text_model.pkl")
vectorizer = joblib.load("text_vectorizer.pkl")

tests = [
    ("AI 1 (Climate Change)", "Understanding climate change is essential in today's rapidly changing world. Climate change and its effects on ecosystems touches on fundamental questions that affect both individuals and society as a whole. From an environmental science perspective, several key mechanisms are at work. Researchers have identified multiple contributing factors, each of which plays a distinct role. Key areas of focus include: 1. Understanding foundational principles 2. Analyzing empirical evidence 3. Evaluating policy implications. In summary, climate change demands careful, evidence-based inquiry."),
    ("AI 2 (AI Paradigm)", "Artificial intelligence represents a paradigm shift in how we approach complex problem-solving. The underlying architecture is designed to be highly scalable and robust. By utilizing distributed networks, it minimizes latency and maximizes throughput. Furthermore, it is important to consider the ethical implications inherent in such systems. Regular audits and transparent methodologies are highly recommended. Ultimately, fostering a collaborative ecosystem will be key to unlocking the full potential of AI."),
    ("AI 3 (Photosynthesis)", "Photosynthesis is a fundamental biological process whereby plants convert sunlight into chemical energy. This process occurs primarily in the chloroplasts, where chlorophyll absorbs light in the red and blue wavelengths. The light-dependent reactions produce ATP and NADPH, which are subsequently used in the Calvin cycle to fix atmospheric carbon dioxide into glucose. Understanding photosynthesis has significant implications for agriculture, biofuel development, and our understanding of the global carbon cycle."),
    ("Human 1 (Gandhi)", "Mahatma Gandhi launched the Non-Cooperation Movement in 1920 to protest against the Rowlatt Act and the Jallianwala Bagh massacre. Thousands of students left government-run schools and colleges, while lawyers gave up their practice in courts. People burnt foreign-made cloth and adopted khadi. The movement gained tremendous momentum across the country."),
    ("Human 2 (Coastal)", "Growing up in a coastal village meant our lives revolved around the ocean tides. Every afternoon when the fishing boats returned to the shore, the beach transformed into a bustling marketplace. Men unloaded nets heavy with pomfret, mackerel, and prawns, while women sorted the catch into wicker baskets."),
    ("Human 3 (Mitochondria)", "Mitochondria are often described as the powerhouse of the cell because they generate most of the chemical energy needed to power cellular biochemical reactions. Energy produced by mitochondria is stored in a small molecule called adenosine triphosphate. The mitochondria of cells that require large amounts of energy, such as muscle cells, are more numerous and have more cristae than those in less active cells."),
]

print("=" * 65)
print(f"{'Sample':<25} | {'Raw ML AI%':<12} | {'Raw ML Human%':<12}")
print("=" * 65)

for label, text in tests:
    v = vectorizer.transform([text])
    p_ai = model.predict_proba(v)[0][1] * 100
    p_human = 100 - p_ai
    print(f"{label:<25} | {p_ai:11.1f}% | {p_human:11.1f}%")
print("=" * 65)
