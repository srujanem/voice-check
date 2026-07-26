from datasets import load_dataset, get_dataset_config_names

try:
    print("Configs for Hello-SimpleAI/HC3:", get_dataset_config_names("Hello-SimpleAI/HC3"))
    ds = load_dataset("Hello-SimpleAI/HC3", "all")
    print("Success loading HC3!")
except Exception as e:
    print(f"Config error: {e}")

try:
    # Try alternative real AI vs Human text dataset on HuggingFace that uses standard Parquet
    ds2 = load_dataset("mteb/tweet_sentiment_extraction")
    print("Test load mteb:", ds2)
except Exception as e:
    print(f"Error 2: {e}")
