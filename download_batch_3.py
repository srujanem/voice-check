import os
import time
import requests
import urllib.parse
import sys

prompts = [
    "A photorealistic close up of a t-rex eye looking through jungle leaves",
    "A beautiful fairy sitting on a glowing mushroom in a dark forest",
    "A massive black hole accreting matter in deep space cinematic",
    "A highly realistic 3D render of a futuristic smart home interior",
    "A majestic phoenix bird made of fire flying through the sky",
    "A photorealistic shot of a busy neon street market in Tokyo cyberpunk style",
    "An old haunted victorian mansion on a hill with lightning 8k",
    "A hyper-realistic portrait of a female android with glowing eyes",
    "A sleek futuristic pistol resting on a metallic table",
    "A highly detailed shot of a pirate ship sailing through a massive storm",
    "A cute golden retriever puppy wearing sunglasses on a beach",
    "A hyper-realistic shot of an erupting volcano with red hot lava",
    "A cinematic wide shot of a medieval city surrounded by a massive wall",
    "A macro shot of a metallic blue morpho butterfly on a vibrant orchid",
    "A photorealistic portrait of an alien ambassador in regal clothing",
    "A hyper-realistic view of the Milky Way from a desert canyon",
    "A highly detailed 3D render of a steampunk submarine exploring a coral reef",
    "A cinematic shot of a samurai standing in a bamboo forest during a snowstorm",
    "A hyper-realistic photograph of an abandoned theme park overgrown with vines",
    "A photorealistic extreme close-up of a vinyl record playing",
    "A sprawling futuristic vertical farm with glowing purple grow lights",
    "A hyper-realistic shot of a lightning strike hitting a skyscraper",
    "A highly detailed oil painting of a kraken attacking a galleon",
    "A cinematic portrait of a post-apocalyptic survivor with a robotic arm",
    "A beautiful bioluminescent beach at night with glowing blue waves"
]

dest_dir = r"D:\voice-check\voice-check\dataset_image\fake"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("Starting background download of 25 new AI images...")
for i, prompt in enumerate(prompts):
    filename = f"ai_batch_3_{i+1:02d}.jpg"
    filepath = os.path.join(dest_dir, filename)
    
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {i+1}/25")
        else:
            print(f"Rate limited on {i+1}, pausing...")
            time.sleep(10) # Heavy pause if rate limited
    except Exception as e:
        pass
    
    # 3 second delay to avoid rate limit
    time.sleep(3)

print("Finished downloading. Running augmentation and training...")
os.system("python augment_ai_images.py")
os.system("python train_image_fixed.py")
os.system("taskkill /F /IM python.exe /T")
