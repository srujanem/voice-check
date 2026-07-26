import requests

repo_url = "https://api.github.com/repos/Hello-SimpleAI/chatgpt-comparison-detection"
r = requests.get(repo_url).json()
default_branch = r.get("default_branch", "master")
print("Default branch:", default_branch)

tree_url = f"https://api.github.com/repos/Hello-SimpleAI/chatgpt-comparison-detection/git/trees/{default_branch}?recursive=1"
r_tree = requests.get(tree_url).json()

for item in r_tree.get("tree", []):
    if item["path"].endswith(".jsonl") or item["path"].endswith(".json") or "HC3" in item["path"]:
        print(" ->", item["path"])
