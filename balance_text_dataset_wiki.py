import os
import urllib.request
import urllib.parse
import json
import random

print("Fetching formal human text directly from Wikipedia API...")

topics = ["Artificial Intelligence", "History of Rome", "Quantum Mechanics", "Economics", "Industrial Revolution", "Evolutionary Biology", "Climate Change", "Philosophy of Mind", "Renaissance Art", "Space Exploration", "Computer Science", "Neuroscience", "Ancient Egypt", "Linguistics", "Macroeconomics", "Organic Chemistry", "Political Science", "Thermodynamics", "Information Theory", "Genetics"]

output_dir = r"D:\voice-check\voice-check\dataset_text\human\formal_wiki"
os.makedirs(output_dir, exist_ok=True)

count = 0
for topic in topics:
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=True&explaintext=True&titles={urllib.parse.quote(topic)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            pages = data['query']['pages']
            for page_id in pages:
                extract = pages[page_id].get('extract', '')
                paragraphs = [p for p in extract.split('\n') if len(p.split()) > 20]
                
                for p in paragraphs:
                    filepath = os.path.join(output_dir, f"wiki_{count:04d}.txt")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(p)
                    count += 1
    except Exception as e:
        print(f"Failed {topic}: {e}")

print(f"Successfully saved {count} formal human texts from Wikipedia.")

# Since that might only be ~100 paragraphs, let's fetch more dynamically using random pages
print("Fetching more from random pages...")
for _ in range(50):
    if count >= 2000: break
    try:
        url = "https://en.wikipedia.org/w/api.php?action=query&format=json&list=random&rnnamespace=0&rnlimit=10"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            for item in data['query']['random']:
                title = item['title']
                
                url2 = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=True&explaintext=True&titles={urllib.parse.quote(title)}"
                req2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req2) as r2:
                    d2 = json.loads(r2.read().decode())
                    p2 = d2['query']['pages']
                    for p_id in p2:
                        ext = p2[p_id].get('extract', '')
                        paras = [pa for pa in ext.split('\n') if len(pa.split()) > 20]
                        for pa in paras:
                            filepath = os.path.join(output_dir, f"wiki_{count:04d}.txt")
                            with open(filepath, "w", encoding="utf-8") as f:
                                f.write(pa)
                            count += 1
    except:
        pass

print(f"Total formal texts saved: {count}")
print("Retraining ensemble model...")
os.system("python train_text_ensemble.py")
print("Restarting backend...")
os.system("taskkill /F /IM python.exe /T")
