import os
import time
import urllib.request
import uuid

FAKE_DIR = r"D:\voice-check\voice-check\dataset_image\fake"
os.makedirs(FAKE_DIR, exist_ok=True)

count = 0
for i in range(100):
    try:
        url = "https://thispersondoesnotexist.com/"
        filepath = os.path.join(FAKE_DIR, f"tpdne_face_{uuid.uuid4().hex[:8]}.jpg")
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(filepath, 'wb') as f:
                f.write(response.read())
                
        count += 1
        print(f"Downloaded {count}/100: {filepath}")
        time.sleep(1.5)  # Politeness delay
        
    except Exception as e:
        print(f"Error downloading image {i}: {e}")
        time.sleep(3)

print(f"Successfully generated {count} AI face images!")
print("Starting training script directly...")
os.system("python train_image_advanced.py")
