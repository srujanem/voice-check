import requests

BASE = "http://localhost:5000"
HEADERS = {"Authorization": ""}

tests = [
    # --- AI texts (should be detected as AI-Generated) ---
    ("AI", "Understanding climate change is essential in today's rapidly changing world. Climate change and its effects on ecosystems touches on fundamental questions that affect both individuals and society as a whole. From an environmental science perspective, several key mechanisms are at work. Researchers have identified multiple contributing factors, each of which plays a distinct role. Key areas of focus include: 1. Understanding foundational principles 2. Analyzing empirical evidence 3. Evaluating policy implications. In summary, climate change demands careful, evidence-based inquiry."),
    
    ("AI", "Artificial intelligence represents a paradigm shift in how we approach complex problem-solving. The underlying architecture is designed to be highly scalable and robust. By utilizing distributed networks, it minimizes latency and maximizes throughput. Furthermore, it is important to consider the ethical implications inherent in such systems. Regular audits and transparent methodologies are highly recommended. Ultimately, fostering a collaborative ecosystem will be key to unlocking the full potential of AI."),
    
    ("AI", "Photosynthesis is a fundamental biological process whereby plants convert sunlight into chemical energy. This process occurs primarily in the chloroplasts, where chlorophyll absorbs light in the red and blue wavelengths. The light-dependent reactions produce ATP and NADPH, which are subsequently used in the Calvin cycle to fix atmospheric carbon dioxide into glucose. Understanding photosynthesis has significant implications for agriculture, biofuel development, and our understanding of the global carbon cycle."),

    # --- Human texts (should be detected as Human Written) ---
    ("Human", "Mahatma Gandhi launched the Non-Cooperation Movement in 1920 to protest against the Rowlatt Act and the Jallianwala Bagh massacre. Thousands of students left government-run schools and colleges, while lawyers gave up their practice in courts. People burnt foreign-made cloth and adopted khadi. The movement gained tremendous momentum across the country."),
    
    ("Human", "Growing up in a coastal village meant our lives revolved around the ocean tides. Every afternoon when the fishing boats returned to the shore, the beach transformed into a bustling marketplace. Men unloaded nets heavy with pomfret, mackerel, and prawns, while women sorted the catch into wicker baskets."),
    
    ("Human", "Mitochondria are often described as the powerhouse of the cell because they generate most of the chemical energy needed to power cellular biochemical reactions. Energy produced by mitochondria is stored in a small molecule called adenosine triphosphate. The mitochondria of cells that require large amounts of energy, such as muscle cells, are more numerous and have more cristae than those in less active cells."),
]

print("=" * 65)
print(f"  {'Expected':<10} {'Got':<20} {'AI%':>6}  {'Human%':>8}  {'Label'}")
print("=" * 65)

correct = 0
for expected, text in tests:
    r = requests.post(f"{BASE}/predict_text", json={"text": text}, headers=HEADERS)
    d = r.json()
    got   = "AI" if d.get("is_ai") else "Human"
    ok    = "OK" if got == expected else "WRONG"
    if got == expected:
        correct += 1
    print(f"  {expected:<10} {got:<20} {d.get('prob_ai','?'):>5}%  {d.get('prob_human','?'):>6}%  [{d.get('confidence_label','')}]  {ok}")

print("=" * 65)
print(f"  Score: {correct}/{len(tests)}  ({correct/len(tests)*100:.0f}%)")
print("=" * 65)
