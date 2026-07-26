import os, glob

human_dir = os.path.join("dataset_text", "human")
ai_dir    = os.path.join("dataset_text", "ai")

all_h = os.listdir(human_dir)
pdf_chunks_deleted = 0

for f in all_h:
    if f.endswith('.txt'):
        try:
            num = int(f.replace('.txt', ''))
            if num > 3000:
                os.remove(os.path.join(human_dir, f))
                pdf_chunks_deleted += 1
        except ValueError:
            pass

h_count = len(os.listdir(human_dir))
a_count = len(os.listdir(ai_dir))

print(f"Deleted {pdf_chunks_deleted} extra PDF chunk files.")
print(f"Clean Dataset Status: {h_count} Human files | {a_count} AI files.")
