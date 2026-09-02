import torch
import os
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import logging

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.disable(logging.WARNING)

print("\n=======================================================")
print("  AUTHGUARD: ADVANCED GPU FINE-TUNING (DeBERTa-V3) ")
print("  - Target: Catch ChatGPT-4o & Claude 3.5")
print("  - Engine: PyTorch + NVIDIA CUDA")
print("=======================================================\n")

print("[1/4] Loading local Secure Dataset...")
dataset = load_dataset('csv', data_files='ai_vs_human_dataset.csv', split='train')

print("[2/4] Tokenizing with Microsoft DeBERTa-V3 (Disentangled Attention)...")
# Upgrading from RoBERTa to DeBERTa-v3-base for significantly higher accuracy
model_name = "microsoft/deberta-v3-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

tokenized_datasets = dataset.map(tokenize_function, batched=True)
split_dataset = tokenized_datasets.train_test_split(test_size=0.1, seed=42)

print("[3/4] Loading DeBERTa Neural Network into RTX 4050 VRAM...")
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

training_args = TrainingArguments(
    output_dir="./text_ai_results_v2",
    num_train_epochs=3,
    per_device_train_batch_size=8, # Reduced to 8 to fit safely in 6GB VRAM
    gradient_accumulation_steps=2, # Simulates batch size of 16
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_steps=50,
    fp16=True, # Mixed precision for RTX 40-series speedup
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=split_dataset["train"],
    eval_dataset=split_dataset["test"],
)

print("\n--- INITIATING PYTORCH GPU FINE-TUNING ---")
trainer.train()

print("\n[4/4] Saving upgraded DeBERTa Model to disk...")
trainer.save_model("model_text_finetuned")
tokenizer.save_pretrained("model_text_finetuned")
print("\nTEXT AI UPGRADE 100% COMPLETE! Your website will automatically load this new model on restart.")
