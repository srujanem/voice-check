import os
from datasets import load_dataset

print("Downloading Real and Fake image starter pack to dataset_custom...")

try:
    ds = load_dataset("Hemg/AI-Generated-vs-Real-Images-Datasets", split="train", streaming=True)
    fake_count = 0
    real_count = 0
    for item in ds:
        img = item['image']
        label = item['label']
        if img.mode != 'RGB': img = img.convert('RGB')
        
        if label == 0 and fake_count < 10: # AiArtData
            img.save(f"D:/voice-check/voice-check/dataset_custom/fake/downloaded_ai_{fake_count}.jpg")
            fake_count += 1
        elif label == 1 and real_count < 10: # RealArt
            img.save(f"D:/voice-check/voice-check/dataset_custom/real/downloaded_real_{real_count}.jpg")
            real_count += 1
            
        if fake_count >= 10 and real_count >= 10:
            break
            
    print("Saved 10 AI-Generated and 10 Real images to your custom dataset folders!")
except Exception as e:
    print("Failed:", e)
