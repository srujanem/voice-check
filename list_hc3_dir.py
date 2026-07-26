import requests

url = "https://api.github.com/repos/Hello-SimpleAI/chatgpt-comparison-detection/contents/HC3"
r = requests.get(url).json()

for item in r:
    print(" ->", item["name"], "(", item["type"], ")")
