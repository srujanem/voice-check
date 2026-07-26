from huggingface_hub import HfApi
api = HfApi()
datasets = api.list_datasets(search="cifake", limit=5)
for d in datasets:
    print(d.id)
    
print("---")
datasets2 = api.list_datasets(search="real vs fake image", limit=5)
for d in datasets2:
    print(d.id)
