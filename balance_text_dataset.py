import os
from datasets import load_dataset
import random

print("Loading AG News dataset for formal human texts...")
dataset = load_dataset("ag_news", split="train")

# Shuffle and pick 2000 random formal news texts
random.seed(42)
indices = random.sample(range(len(dataset)), 2000)

output_dir = r"D:\voice-check\voice-check\dataset_text\human\formal_news"
os.makedirs(output_dir, exist_ok=True)

print("Saving 2000 formal human texts...")
count = 0
for idx in indices:
    text = dataset[idx]['text']
    # Clean up some basic AG news weirdness (like leading category names)
    text = text.replace('\\', ' ')
    
    if len(text.split()) > 10:
        filepath = os.path.join(output_dir, f"formal_{count:04d}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        count += 1

print(f"Successfully saved {count} formal human texts.")

print("Retraining ensemble model...")
os.system("python train_text_ensemble.py")
print("Restarting backend...")
os.system("taskkill /F /IM python.exe /T")
