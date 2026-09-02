import os
inference_path = r'D:\Server\ai-training-panel\python_engine\inference.py'

with open(inference_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Image Inference path
content = content.replace(r'C:\voice-check\model_image.keras', r'D:\voice-check\voice-check\model_image_best_grid.keras')

with open(inference_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated inference.py to use model_image_best_grid.keras")
