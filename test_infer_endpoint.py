import requests

BASE = "http://127.0.0.1:5000"

text_ai = "In today's fast-paced world, artificial intelligence plays a crucial role in modern technology. It fosters innovation across various sectors including healthcare, finance, and education."
text_human = "Photosynthesis is the process by which green plants transform light energy into chemical energy. During photosynthesis in green plants, light energy is captured."

print("Testing /api/infer for AI text...")
r1 = requests.post(f"{BASE}/api/infer", data={"type": "text", "text": text_ai})
print("AI Response:", r1.json())

print("\nTesting /api/infer for Human text...")
r2 = requests.post(f"{BASE}/api/infer", data={"type": "text", "text": text_human})
print("Human Response:", r2.json())
