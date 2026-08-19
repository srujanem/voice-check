import os
import time
import requests
import urllib.parse
import random
import sys

subjects = [
    "A soaring bald eagle", "A classical greek marble statue", "An alien spacecraft", 
    "A cute baby Yoda-like creature", "An intricate pocket watch", "A glowing magical sword", 
    "A roaring grizzly bear", "A futuristic combat drone", "A vintage 1950s diner", 
    "A mysterious cloaked figure", "A herd of wild mustangs", "A delicious pepperoni pizza", 
    "A massive ocean liner", "A cybernetic geisha", "A wise talking tree", "A neon lit jukebox", 
    "A knight in shining armor", "A crystal skull", "A cute cartoon penguin", "A massive coral reef",
    "A deep space astronaut", "A steampunk locomotive", "A giant mechanical spider", "A majestic pegasus",
    "A grumpy looking bulldog", "A beautiful geode crystal", "A futuristic neon motorcycle"
]
styles = [
    "hyper-realistic 8k", "claymation style", "intricate voxel art", 
    "classical watercolor painting", "cinematic lighting", "matte painting", 
    "anime Studio Ghibli style", "dark gritty comic book style", "synthwave neon style", 
    "professional architectural photography"
]
settings = [
    "in a bustling cyberpunk metropolis", "in an ancient ruined temple", "floating in a colorful nebula", 
    "underwater amidst glowing jellyfish", "on a desolate red planet", 
    "in a sunny suburban neighborhood", "during a massive thunderstorm with lightning", 
    "inside a cozy rustic tavern", "on top of a skyscraper at night", 
    "in a lush tropical jungle"
]

prompts = []
for _ in range(100):
    prompts.append(f"{random.choice(subjects)} {random.choice(settings)}, {random.choice(styles)}")

dest_dir = r"D:\voice-check\voice-check\dataset_image\fake"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0'}

print("Starting generation of 100 MORE unique AI images...")
success = 0
for i, prompt in enumerate(prompts):
    filename = f"ai_batch_4_{i+1:03d}.jpg"
    filepath = os.path.join(dest_dir, filename)
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true"
    
    retries = 3
    while retries > 0:
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                print(f"Downloaded {i+1}/100")
                sys.stdout.flush()
                success += 1
                break
            elif resp.status_code == 429:
                print(f"Rate limited on {i+1}. Sleeping 15 seconds...")
                sys.stdout.flush()
                time.sleep(15)
            else:
                break
        except Exception as e:
            pass
        retries -= 1
        
    time.sleep(3.5) # Safe delay between downloads

print(f"Finished downloading {success} images. Starting augmentation...")
sys.stdout.flush()
os.system("python augment_ai_images.py")
print("Starting training...")
sys.stdout.flush()
os.system("python train_image_fixed.py")
print("Restarting server...")
sys.stdout.flush()
os.system("taskkill /F /IM python.exe /T")
