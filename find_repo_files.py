import requests

url = "https://api.github.com/repos/Hello-SimpleAI/chatgpt-comparison-detection/git/trees/main?recursive=1"
r = requests.get(url).json()

print("Files in repo:")
for item in r.get("tree", []):
    if item["path"].endswith(".jsonl") or item["path"].endswith(".json"):
        print(" ->", item["path"])
