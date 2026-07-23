import torch
import numpy as np
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

print("Loading distilgpt2 model for Perplexity scoring...")
model_id = "distilgpt2"
tokenizer = GPT2TokenizerFast.from_pretrained(model_id)
model = GPT2LMHeadModel.from_pretrained(model_id)
model.eval()

def compute_perplexity(text):
    encodings = tokenizer(text, return_tensors="pt")
    input_ids = encodings.input_ids
    
    if input_ids.shape[1] < 5:
        return 100.0, 0.0  # Default fallback for tiny text
        
    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
        neg_log_likelihood = outputs.loss
        
    ppl = torch.exp(neg_log_likelihood).item()
    return ppl

# Test on AI vs Human text
human_sample = "Honestly I didn't think it would work out that way lol. Was pretty surprised when they announced the changes yesterday!"
ai_sample = "In conclusion, artificial intelligence represents a transformative technology that promises to revolutionize numerous sectors. Furthermore, its ethical implications must be carefully navigated to foster a sustainable future."

print(f"Human PPL: {compute_perplexity(human_sample):.2f}")
print(f"AI PPL   : {compute_perplexity(ai_sample):.2f}")
