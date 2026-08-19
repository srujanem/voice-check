import os
import time
import requests
import urllib.parse
import random
import sys

subjects = [
    "A majestic lion", "A futuristic cyborg", "A cute red panda", "An ancient dragon", 
    "A neon sports car", "A wise old wizard", "A lone samurai", "A glowing jellyfish", 
    "A steampunk airship", "A massive mecha robot", "A cybernetic hacker", "A space marine", 
    "A golden retriever", "A creepy haunted doll", "A giant glowing mushroom", "A luxury watch", 
    "A shiny samurai sword", "A cyberpunk hovercar", "A massive floating castle", "A mystical unicorn",
    "A deep sea angler fish", "A beautiful female android", "A fiery phoenix", "A robotic dog",
    "A spooky grim reaper"
]
styles = [
    "photorealistic", "cinematic 8k resolution", "classical oil painting style", 
    "highly detailed Pixar 3D render", "extreme macro photography", "epic concept art", 
    "vintage 1920s film noir photo", "neon synthwave aesthetic", "dark fantasy style", 
    "professional studio portrait lighting"
]
settings = [
    "in a rainy cyberpunk city", "in a dense magical forest", "floating in deep space nebulas", 
    "underwater in a vibrant coral reef", "on the surface of an alien planet with two moons", 
    "in a dusty post-apocalyptic wasteland", "during a beautiful fiery sunset", 
    "inside a sleek futuristic laboratory", "on top of a freezing snowy mountain peak", 
    "in a peaceful traditional Japanese zen garden"
]

prompts = []
for _ in range(100):
    prompts.append(f"{random.choice(subjects)} {random.choice(settings)}, {random.choice(styles)}")

dest_dir = r"D:\voice-check\voice-check\dataset_image\fake"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

print("Starting generation of 100 unique AI images...")
success = 0
for i, prompt in enumerate(prompts):
    filename = f"ai_batch_100_{i+1:03d}.jpg"
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
