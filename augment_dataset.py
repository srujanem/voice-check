import pandas as pd
from datasets import load_dataset
import os

print("==================================================")
print("  AUGMENTING DATASET WITH HIGH-QUALITY EXAMPLES  ")
print("==================================================")

# 1. Load the current dataset
existing_file = 'ai_vs_human_dataset.csv'
if os.path.exists(existing_file):
    df_existing = pd.read_csv(existing_file)
    print(f"Current dataset size: {len(df_existing)} rows")
else:
    print("Could not find existing dataset!")
    exit(1)

# 2. Download a high-quality AI/Human dataset from HuggingFace
# 'Hello-SimpleAI/HC3' contains high quality ChatGPT vs Human answers
print("Downloading additional dataset from HuggingFace (dmitva/human_ai_generated_text)...")
try:
    dataset = load_dataset("dmitva/human_ai_generated_text", split="train")
    
    new_data = []
    # We will extract 5000 human answers and 5000 ChatGPT answers
    human_count = 0
    ai_count = 0
    
    for row in dataset:
        if human_count < 5000 and 'human_text' in row and row['human_text']:
            new_data.append({"text": row['human_text'], "label": 0})
            human_count += 1
        if ai_count < 5000 and 'ai_text' in row and row['ai_text']:
            new_data.append({"text": row['ai_text'], "label": 1})
            ai_count += 1
            
        if human_count >= 5000 and ai_count >= 5000:
            break

    df_new = pd.DataFrame(new_data)
    
    # 3. Merge and Shuffle
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined = df_combined.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save back to disk
    df_combined.to_csv(existing_file, index=False)
    print(f"\n✅ Dataset successfully expanded!")
    print(f"New Total Size: {len(df_combined)} rows")
    print(df_combined['label'].value_counts())
    
except Exception as e:
    print(f"Failed to augment dataset: {e}")
