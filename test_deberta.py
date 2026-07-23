from transformers import pipeline

print("Loading RoBERTa AI Text Detection model...")
detector = pipeline("text-classification", model="roberta-base-openai-detector")

human_text = "I went to the store this morning and bought some fresh apples and bread. The weather was really nice outside."
ai_text = "Furthermore, it is important to emphasize that artificial intelligence represents a pivotal shift in modern technological landscapes."

print("Human prediction:", detector(human_text))
print("AI prediction   :", detector(ai_text))
