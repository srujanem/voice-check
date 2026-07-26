from datasets import load_dataset

datasets_to_try = [
    "artiezer/HC3",
    "NicolaiSoren/ai-vs-human-text",
    "davanstru/human_ai_generated_text",
    "daigt/v2-train-dataset"
]

for name in datasets_to_try:
    try:
        ds = load_dataset(name)
        print(f"Success loading {name}: {ds}")
        break
    except Exception as e:
        print(f"Failed {name}: {e}")
