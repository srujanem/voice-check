import numpy as np, re, math

def calculate_stylometric_features(text):
    words = text.split()
    if not words:
        return {"burstiness": 0, "ttr": 0, "connector_score": 0, "ai_score": 0}
    
    # 1. Sentence length variance (Burstiness)
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sent_lengths = [len(s.split()) for s in sentences if len(s.split()) > 0]
    
    if len(sent_lengths) >= 2:
        mean_len = np.mean(sent_lengths)
        std_len  = np.std(sent_lengths)
        burstiness = (std_len - mean_len) / (std_len + mean_len + 1e-5)
    else:
        burstiness = 0.0

    # 2. Type-Token Ratio (Lexical Diversity)
    unique_words = set(w.lower() for w in words)
    ttr = len(unique_words) / len(words)

    # 3. Formal Discourse Connectors & AI Watermarks
    connectors = [
        r"\b(furthermore|moreover|consequently|additionally|in conclusion|in summary)\b",
        r"\b(it is (worth|important|crucial|essential) to (note|highlight|understand|consider))\b",
        r"\b(plays a (crucial|vital|pivotal|key|paramount) role)\b",
        r"\b(in today'?s (fast-paced|rapidly changing|digital|modern) world)\b",
        r"\b(delve|intricate|tapestry|testament|fosters|underscores|multifaceted)\b",
        r"\b(overall|to summarize|as a result|on the other hand|it should be noted)\b"
    ]
    
    connector_matches = 0
    text_lower = text.lower()
    for pat in connectors:
        if re.search(pat, text_lower):
            connector_matches += 1

    # Composite Generalized AI Score (0.0 to 1.0)
    ai_points = 0.0
    
    # AI tends to have low burstiness (uniform sentence lengths)
    if len(sent_lengths) >= 3 and std_len < 4.5:
        ai_points += 0.25
        
    # AI tends to have TTR between 0.60 and 0.82
    if 0.60 <= ttr <= 0.82 and len(words) >= 15:
        ai_points += 0.20
        
    # Formal connectors
    if connector_matches >= 2:
        ai_points += 0.45
    elif connector_matches == 1:
        ai_points += 0.25
        
    return {
        "burstiness": round(float(burstiness), 3),
        "ttr": round(float(ttr), 3),
        "connector_matches": connector_matches,
        "ai_score": round(float(ai_points), 3)
    }

# Test unseen samples
test_samples = [
    ("Climate change poses severe risks to global ecosystems. Rising sea levels and extreme weather events threaten coastal communities and biodiversity.", "AI"),
    ("Hey man, I was walking down the street yesterday and saw this crazy accident! Everyone was shouting and calling 911.", "Human"),
    ("Quantum mechanics is a physical science dealing with the behavior of matter and energy on atomic scales.", "Human/Textbook"),
    ("Furthermore, it is essential to consider the multifaceted nature of digital transformation in modern business operations.", "AI"),
    ("I don't think that's a good idea at all. We tried it last week and it totally failed.", "Human"),
    ("In summary, adopting renewable energy sources plays a pivotal role in reducing carbon emissions globally.", "AI")
]

print("="*75)
print(f"{'Sample Text':<50} | {'TTR':<5} | {'Conn':<4} | {'AI Score'}")
print("="*75)

for text, label in test_samples:
    res = calculate_stylometric_features(text)
    print(f"{text[:48]:<50} | {res['ttr']:<5} | {res['connector_matches']:<4} | {res['ai_score']}")

print("="*75)
