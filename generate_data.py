import pandas as pd
import random

# Generate a synthetic dataset for demonstration of AI vs Human text
# In a real environment, you'd pull this from a 50GB Parquet dump of Claude/GPT text.
human_texts = [
    "I really think that we should focus on the main character's development. It felt rushed.",
    "Hey everyone, just wanted to share my thoughts on the new update. It's pretty good overall.",
    "Can someone help me figure out why my code is throwing a null pointer exception?",
    "I had a great time at the concert last night. The band was amazing and the crowd was hype.",
    "Honestly, I'm not a fan of the new design. It feels clunky and hard to navigate."
]

ai_texts = [
    "In conclusion, the multifaceted nature of this issue requires a comprehensive approach.",
    "Certainly! Here is a detailed breakdown of the null pointer exception and how to fix it:",
    "It is important to note that the implications of this study reach far beyond the initial scope.",
    "As an AI language model, I don't have personal opinions, but I can summarize the main points.",
    "The seamless integration of these technologies provides a robust framework for future growth."
]

data = []
for _ in range(2500):
    data.append({"text": random.choice(human_texts) + " " + random.choice(human_texts), "label": 0})
    data.append({"text": random.choice(ai_texts) + " " + random.choice(ai_texts), "label": 1})

df = pd.DataFrame(data)
df.to_csv("ai_vs_human_dataset.csv", index=False)
print("Synthetic Dataset Generated: ai_vs_human_dataset.csv (5000 rows)")
