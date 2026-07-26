from datasets import load_dataset
import sys

try:
    print("Testing dragonintelligence/CIFAKE-image-dataset...")
    ds = load_dataset("dragonintelligence/CIFAKE-image-dataset", split="train", streaming=True)
    for item in ds:
        print(item)
        break
except Exception as e:
    print(f"Error: {e}")
