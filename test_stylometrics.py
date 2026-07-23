import numpy as np
import re

AI_MARKER_WORDS = {
    "furthermore", "moreover", "additionally", "consequently", "in conclusion",
    "it is important to note", "delve", "tapestry", "pivotal", "underscores",
    "fosters", "testament", "realm", "multifaceted", "paramount", "imperative",
    "crucial", "beacon", "intertwined", "vibrant", "holistic", "seamlessly"
}

HUMAN_CONTRACTIONS = {
    "can't", "don't", "won't", "isn't", "aren't", "wasn't", "weren't",
    "haven't", "hasn't", "hadn't", "doesn't", "didn't", "couldn't",
    "shouldn't", "wouldn't", "it's", "i'm", "they're", "we're", "you're",
    "i've", "you've", "we've", "they've", "i'd", "you'd", "he'd", "she'd"
}

def extract_stylometric_features(text):
    words = text.split()
    total_words = max(1, len(words))
    
    # 1. Sentence burstiness (std dev of sentence lengths)
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    sentence_lengths = [len(s.split()) for s in sentences] if sentences else [total_words]
    mean_sent_len = np.mean(sentence_lengths)
    std_sent_len  = np.std(sentence_lengths) if len(sentence_lengths) > 1 else 0.0
    
    # 2. Vocabulary richness (Type-Token Ratio)
    unique_words = len(set(w.lower() for w in words))
    ttr = unique_words / total_words
    
    # 3. Average word length
    mean_word_len = np.mean([len(w) for w in words]) if words else 0.0
    
    # 4. AI Transition marker density
    text_lower = text.lower()
    ai_marker_count = sum(text_lower.count(marker) for marker in AI_MARKER_WORDS)
    ai_marker_density = ai_marker_count / total_words
    
    # 5. Human contraction density
    contraction_count = sum(text_lower.count(c) for c in HUMAN_CONTRACTIONS)
    contraction_density = contraction_count / total_words
    
    # 6. Punctuation densities
    comma_count = text.count(',') / total_words
    semicolon_count = text.count(';') / total_words
    quote_count = (text.count('"') + text.count("'")) / total_words
    
    return [
        mean_sent_len,
        std_sent_len,       # Burstiness
        ttr,                # Vocabulary richness
        mean_word_len,
        ai_marker_density,
        contraction_density,
        comma_count,
        semicolon_count,
        quote_count
    ]

# Quick test
sample_human = "Hey guys! Can't wait for tonight. I'm leaving in 5 mins. It's gonna be awesome!"
sample_ai = "Furthermore, it is important to note that the multifaceted nature of this ecosystem underscores a pivotal shift. Consequently, a holistic approach is paramount."

print("Human features:", extract_stylometric_features(sample_human))
print("AI features   :", extract_stylometric_features(sample_ai))
