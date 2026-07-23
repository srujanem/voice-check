import requests
import pandas as pd

datasets_to_check = [
    "Hello-SimpleAI/HC3",
    "davanstru/human_ai_generated_text",
    "daigt/v2-train-dataset",
    "argugrid/ai-generated-text-detection"
]

for name in datasets_to_check:
    url = f"https://huggingface.co/api/datasets/{name}/parquet"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            config = list(data.keys())[0]
            first_file = data[config]['train'][0]
            df = pd.read_parquet(first_file)
            print(f"[OK] {name}: {len(df)} rows | columns={df.columns.tolist()[:4]}")
        else:
            print(f"[FAIL] {name}: HTTP {r.status_code}")
    except Exception as e:
        print(f"[ERR] {name}: {e}")
