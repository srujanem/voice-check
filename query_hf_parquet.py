import requests
import pandas as pd

api_url = "https://huggingface.co/api/datasets/Hello-SimpleAI/HC3/parquet"
print(f"Querying HF parquet API: {api_url}")

r = requests.get(api_url)
print("Status code:", r.status_code)
if r.status_code == 200:
    data = r.json()
    print("Configs:", list(data.keys()))
    if "all" in data:
        print("Parquet files for 'all':", data["all"]["train"])
        parquet_url = data["all"]["train"][0]
        df = pd.read_parquet(parquet_url)
        print(f"Successfully loaded Parquet with {len(df)} rows!")
        print("Columns:", df.columns.tolist())
        print("Sample human answer:", df.iloc[0]['human_answers'][0][:100])
        print("Sample ChatGPT answer:", df.iloc[0]['chatgpt_answers'][0][:100])
