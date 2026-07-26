import os, joblib, torch, re, numpy as np
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

vectorizer = joblib.load("text_vectorizer.pkl")
model      = joblib.load("text_model.pkl")

tokenizer = GPT2TokenizerFast.from_pretrained("distilgpt2")
gpt2_model = GPT2LMHeadModel.from_pretrained("distilgpt2")
gpt2_model.eval()

def get_perplexity(text):
    tokens = tokenizer(text, return_tensors="pt")
    input_ids = tokens.input_ids
    if input_ids.shape[1] < 5: return 50.0
    with torch.no_grad():
        outputs = gpt2_model(input_ids, labels=input_ids)
        loss = outputs.loss
        return torch.exp(loss).item()

test_cases = [
    ("AI ChatGPT", "Photosynthesis is a fundamental biological process through which green plants, algae, and certain bacteria convert light energy into chemical energy."),
    ("NCERT Bio Textbook", "Photosynthesis is the process by which green plants transform light energy into chemical energy. During photosynthesis in green plants, light energy is captured."),
    ("AI ChatGPT", "In today's fast-paced world, artificial intelligence plays a crucial role in modern technology. It fosters innovation across various sectors."),
    ("NCERT History Textbook", "The French Revolution began in 1789 when the Third Estate declared itself the National Assembly. This marked the beginning of a transformation."),
    ("Human Casual", "Hey guys, what do you think is the best way to prepare for exams without getting stressed out? I have been trying to study late at night."),
    ("NCERT Physics Textbook", "Electric current is defined as the rate of flow of electric charges through a conductor per unit time. SI unit of electric current is ampere."),
    ("AI ChatGPT Filler", "Furthermore, it is essential to delve into the intricate nuances of this multifaceted topic to fully understand its far-reaching implications."),
    ("Human Personal", "I went to the grocery store yesterday and bought some fresh apples, but when I got home I realized two of them were bruised.")
]

print("="*85)
print(f"{'Type':<22} | {'ML AI%':<8} | {'ML Hum%':<8} | {'PPL':<6} | {'Text Snippet'}")
print("="*85)

for expected, text in test_cases:
    feats = vectorizer.transform([text])
    probs = model.predict_proba(feats)[0]
    ai_prob  = float(probs[1]) * 100
    hum_prob = float(probs[0]) * 100
    ppl = get_perplexity(text)
    print(f"{expected:<22} | {ai_prob:5.1f}%   | {hum_prob:5.1f}%   | {ppl:5.1f} | {text[:35]}...")

print("="*85)
