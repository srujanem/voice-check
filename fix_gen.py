import os
import time
import urllib.request
import urllib.parse
import random
import uuid

FAKE_DIR = r"D:\voice-check\voice-check\dataset_image\fake"
os.makedirs(FAKE_DIR, exist_ok=True)

subjects = ["A cyberpunk city street at night in the rain", "A hyper-realistic portrait of an elderly man with deep wrinkles", 
           "A cinematic shot of a majestic lion on a cliff", "A futuristic flying car parked in a neon garage", 
           "A macro photograph of a dew drop on a bright green leaf", "A glowing mushroom in a dark mystical forest",
           "An astronaut drinking coffee on the moon", "A beautifully plated gourmet dessert at a Michelin star restaurant",
           "A golden retriever playing in the snow", "A medieval knight in shining armor standing in a battlefield"]

styles = ["photorealistic, 8k, highly detailed, sharp focus", "cinematic lighting, Unreal Engine 5 render, dramatic", 
          "shot on 35mm lens, depth of field, real life photograph", "National Geographic photography style"]

count = 0
for i in range(10): # We only need a few more to hit 50, but let's do 10 to be safe
    try:
        prompt = f"{random.choice(subjects)}, {random.choice(styles)}, {random.randint(1000, 9999)}"
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"
        
        filepath = os.path.join(FAKE_DIR, f"pollinations_50_{uuid.uuid4().hex[:8]}.jpg")
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        # ADDED TIMEOUT OF 10 SECONDS TO PREVENT HANGING
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(filepath, 'wb') as f:
                f.write(response.read())
                
        count += 1
        print(f"Downloaded extra {count}: {filepath}")
        time.sleep(2)
        
    except Exception as e:
        print(f"Error downloading image {i}: {e}")
        time.sleep(2)

print(f"Successfully generated {count} AI images!")
