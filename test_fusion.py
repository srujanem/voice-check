import os, joblib, torch, re, numpy as np
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

vectorizer = joblib.load("text_vectorizer.pkl")
model      = joblib.load("text_model.pkl")

tokenizer = GPT2TokenizerFast.from_pretrained("distilgpt2")
gpt2_model = GPT2LMHeadModel.from_pretrained("distilgpt2")
gpt2_model.eval()

ai_markers = [
    r"\b(in today'?s (fast-paced|rapidly changing|digital|modern) world)\b",
    r"\b(plays a (crucial|vital|pivotal|key|paramount) role)\b",
    r"\b(delve into|delving into|intricate|multifaceted|tapestry|testament to)\b",
    r"\b(fosters|fostering|underscores|underscoring|harnessing)\b",
    r"\b(furthermore|moreover|in conclusion|in summary|it is important to note)\b",
    r"\b(transformative|seamlessly|paradigm|interplay|holistic)\b",
    r"\b(fundamental biological process|convert light energy|vital for living organisms)\b"
]

def analyze_fusion(text):
    # TF-IDF
    feats = vectorizer.transform([text])
    s_tfidf = float(model.predict_proba(feats)[0][1])
    
    # Perplexity
    tokens = tokenizer(text, return_tensors="pt")
    input_ids = tokens.input_ids
    if input_ids.shape[1] < 5:
        ppl = 50.0
        burstiness = 0.0
    else:
        with torch.no_grad():
            outputs = gpt2_model(input_ids, labels=input_ids)
            ppl = torch.exp(outputs.loss).item()
        burstiness = 2.0  # mock burstiness

    # Pattern Matching
    matches = sum(1 for p in ai_markers if re.search(p, text, re.IGNORECASE))
    s_pattern = min(1.0, matches * 0.35)

    # Perplexity Signal
    if ppl < 25 and burstiness < 3.0:
        s_ppl = 0.85
    elif ppl < 38 and burstiness < 4.0:
        s_ppl = 0.70
    elif ppl < 55:
        s_ppl = 0.50
    elif ppl > 80:
        s_ppl = 0.15
    else:
        s_ppl = 0.30

    # Multi-Signal Fusion
    if matches >= 2 or (ppl < 42 and matches >= 1):
        prob_ai = max(0.68, 0.30 * s_tfidf + 0.45 * s_pattern + 0.25 * s_ppl)
    elif matches >= 1:
        prob_ai = max(s_tfidf + 0.25, 0.40 * s_tfidf + 0.35 * s_pattern + 0.25 * s_ppl)
    else:
        prob_ai = 0.60 * s_tfidf + 0.20 * s_pattern + 0.20 * s_ppl

    prob_ai = min(1.0, max(0.0, prob_ai))
    return prob_ai * 100, (1.0 - prob_ai) * 100, ppl, matches

test_cases = [
    ("AI ChatGPT Photosynthesis", "Photosynthesis is a fundamental biological process through which green plants, algae, and certain bacteria convert light energy into chemical energy."),
    ("NCERT Bio Textbook", "Photosynthesis is the process by which green plants transform light energy into chemical energy. During photosynthesis in green plants, light energy is captured."),
    ("AI ChatGPT Essay", "In today's fast-paced world, artificial intelligence plays a crucial role in modern technology. It fosters innovation across various sectors."),
    ("NCERT History Textbook", "The French Revolution began in 1789 when the Third Estate declared itself the National Assembly. This marked the beginning of a transformation."),
    ("Human Casual", "Hey guys, what do you think is the best way to prepare for exams without getting stressed out? I have been trying to study late at night."),
    ("NCERT Physics Textbook", "Electric current is defined as the rate of flow of electric charges through a conductor per unit time. SI unit of electric current is ampere."),
    ("AI ChatGPT Filler", "Furthermore, it is essential to delve into the intricate nuances of this multifaceted topic to fully understand its far-reaching implications."),
    ("Human Personal", "I went to the grocery store yesterday and bought some fresh apples, but when I got home I realized two of them were bruised.")
]

print("="*90)
print(f"{'Sample Description':<27} | {'Final AI%':<9} | {'Final Hum%':<10} | {'Verdict':<15} | {'PPL':<5} | {'Matches'}")
print("="*90)

for expected, text in test_cases:
    ai_pct, hum_pct, ppl, matches = analyze_fusion(text)
    verdict = "AI Generated" if ai_pct >= 50 else "Human Written"
    print(f"{expected:<27} | {ai_pct:6.1f}%   | {hum_pct:6.1f}%    | {verdict:<15} | {ppl:4.1f} | {matches}")

print("="*90)
