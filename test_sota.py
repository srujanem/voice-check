import torch
from transformers import pipeline

print('Loading RoBERTa AI Detector...')
try:
    pipe = pipeline('text-classification', model='roberta-base-openai-detector', device=0 if torch.cuda.is_available() else -1)
    res = pipe('Machine learning is a fascinating field of artificial intelligence.')
    print('Inference success:', res)
except Exception as e:
    print('Error:', e)
