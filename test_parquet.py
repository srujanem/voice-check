import pandas as pd
from datasets import load_dataset

print("Testing direct Parquet download from HF...")
url = "https://huggingface.co/datasets/Hello-SimpleAI/HC3/resolve/main/all/train-00000-of-00001.parquet"

try:
    df = pd.read_parquet(url)
    print(f"Success! Downloaded Parquet with {len(df)} rows.")
    print("Columns:", df.columns.tolist())
    print("Sample row:")
    print("Human answer:", df.iloc[0]['human_answers'][:100])
    print("ChatGPT answer:", df.iloc[0]['chatgpt_answers'][:100])
except Exception as e:
    print(f"Error: {e}")
