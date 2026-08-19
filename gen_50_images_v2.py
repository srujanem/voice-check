import os
import urllib.request
import time
import random

DEST_DIR = r"D:\voice-check\voice-check\dataset_image\fake"
os.makedirs(DEST_DIR, exist_ok=True)

prompts = [
    "hyper realistic cyberpunk city 8k resolution",
    "a portrait of a beautiful woman with glowing neon eyes cinematic",
    "futuristic sports car driving on mars unreal engine 5",
    "a giant ancient tree with glowing blue leaves mystical",
    "astronaut riding a horse on the moon photorealistic",
    "steampunk coffee machine extremely detailed 4k",
    "a cute fluffy alien pet playing with a ball",
    "dark fantasy knight with flaming sword dark souls style",
    "macro photography of a mechanical spider",
    "cybernetic brain floating in liquid scifi concept"
]

print("Downloading 50 new AI images...")
for i in range(50):
    prompt = random.choice(prompts) + " variation " + str(random.randint(1, 10000))
    url_prompt = prompt.replace(' ', '%20')
    url = f"https://image.pollinations.ai/prompt/{url_prompt}?width=512&height=512&nologo=true"
    
    filename = os.path.join(DEST_DIR, f"pollinations_ai_batch5_{i+1}.jpg")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req) as response, open(filename, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Downloaded {i+1}/50")
        time.sleep(1)
    except Exception as e:
        print(f"Failed {i+1}: {e}")

print("Generation complete.")
