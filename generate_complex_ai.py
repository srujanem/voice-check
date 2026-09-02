import os
import urllib.request
import urllib.parse
import uuid
import time
import subprocess
import sys

FAKE_DIR = r"D:\voice-check\voice-check\dataset_image\fake"
os.makedirs(FAKE_DIR, exist_ok=True)

prompts = [
    "Narendra Modi and a young man holding Indian flags, Happy Independence Day 15th August text, photorealistic",
    "A political rally in India, huge crowd, politicians on stage holding flags with text 'VOTE NOW', highly detailed",
    "A hyper-realistic poster with the text 'WELCOME TO INDIA', people in traditional clothes, highly detailed",
    "A news broadcast showing a politician speaking, news ticker at the bottom with text, 8k resolution, cinematic",
    "A photorealistic image of a group of people holding a banner that says 'PEACE AND PROSPERITY', detailed faces",
    "An AI generated portrait of an Indian politician, complex background with flags and the text 'INDIA'",
    "A fake newspaper front page with the headline 'ELECTION RESULTS' and a photo of a leader, highly detailed",
    "A realistic photo of people celebrating Independence Day in New Delhi, holding signs with text, 4k",
    "A cinematic shot of a political debate on TV, graphics and text on the screen, highly detailed",
    "A highly detailed magazine cover featuring a political figure with the text 'MAN OF THE YEAR'",
    "A deepfake image of a politician at a press conference, microphone, text on podium, hyperrealistic",
    "An AI generated selfie of two famous politicians, high quality smartphone camera, text in background",
    "A photorealistic election campaign billboard with political symbols and hindi text, bustling street",
    "A crowd of supporters holding placards with complex text, high quality photography",
    "A news reporter holding a microphone with a news channel logo, text overlay breaking news"
]

styles = [
    ", ultra realistic, 8k, sharp focus, photography",
    ", shot on DSLR, hyperdetailed, photorealistic",
    ", news footage style, highly detailed, sharp",
    ", cinematic lighting, unreal engine 5 render, highly detailed"
]

print("Downloading remaining complex AI images to trick the AI...")
sys.stdout.flush()

for i in range(37):
    base_prompt = prompts[i % len(prompts)]
    style = styles[i % len(styles)]
    seed = uuid.uuid4().hex[:6]
    prompt = f"{base_prompt}{style} seed:{seed}"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
    
    filename = os.path.join(FAKE_DIR, f"complex_ai_batch2_{seed}.jpg")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req) as response, open(filename, 'wb') as out_file:
            out_file.write(response.read())
        print(f"[{i+1}/37] Saved {filename}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    sys.stdout.flush()
    time.sleep(2)

print("\nFinished gathering complex AI images!")
sys.stdout.flush()

print("\nStarting PyTorch ViT Training...")
sys.stdout.flush()
subprocess.run(["python", "-u", "train_vit_gpu.py"])

print("\nStarting TensorFlow Training...")
sys.stdout.flush()
subprocess.run(["python", "-u", "train_image_advanced.py"])

print("\nALL UPGRADES COMPLETE!")
sys.stdout.flush()
