import os
from datasets import load_dataset
from PIL import Image

print("Downloading 100 AI and 100 Real images from HuggingFace to dataset_custom...")

fake_dir = "D:/voice-check/voice-check/dataset_custom/fake"
real_dir = "D:/voice-check/voice-check/dataset_custom/real"
os.makedirs(fake_dir, exist_ok=True)
os.makedirs(real_dir, exist_ok=True)

try:
    ds = load_dataset("Hemg/AI-Generated-vs-Real-Images-Datasets", split="train", streaming=True)
    fake_count = 0
    real_count = 0
    
    for item in ds:
        img = item['image']
        label = item['label']
        
        # Convert to RGB to avoid palette issues
        if img.mode != 'RGB': 
            img = img.convert('RGB')
        
        # AiArtData = 0, RealArt = 1
        if label == 0 and fake_count < 100:
            img.save(os.path.join(fake_dir, f"ai_gen_{fake_count}.jpg"))
            fake_count += 1
            if fake_count % 20 == 0:
                print(f"Downloaded {fake_count}/100 Fake images...")
                
        elif label == 1 and real_count < 100:
            img.save(os.path.join(real_dir, f"real_{real_count}.jpg"))
            real_count += 1
            if real_count % 20 == 0:
                print(f"Downloaded {real_count}/100 Real images...")
                
        if fake_count >= 100 and real_count >= 100:
            break
            
    print("SUCCESS: 100 AI images and 100 Real images have been populated in your folders!")
except Exception as e:
    print("Error during download:", e)
