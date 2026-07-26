import requests
import json

url = "https://raw.githubusercontent.com/Hello-SimpleAI/chatgpt-comparison-detection/main/data/all.jsonl"
print(f"Testing stream from {url}...")

r = requests.get(url, stream=True)
print(f"Status code: {r.status_code}")

count = 0
for line in r.iter_lines():
    if line:
        data = json.loads(line)
        count += 1
        if count == 1:
            print("First item keys:", data.keys())
            print("Human answer snippet:", data['human_answers'][0][:80])
            print("ChatGPT answer snippet:", data['chatgpt_answers'][0][:80])
        if count >= 5:
            break

print(f"Success! Read {count} items.")
