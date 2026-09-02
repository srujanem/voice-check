import torch
import os
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import logging

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.disable(logging.WARNING)

print("\n=======================================================")
print("  AUTHGUARD: INITIATING TEXT AI GPU FINE-TUNING ")
print("  - Target: Catch ChatGPT-4o & Claude 3.5")
print("  - Engine: PyTorch + NVIDIA CUDA")
print("=======================================================\n")

print("[1/4] Loading local Secure Dataset (Bypassing HuggingFace script blocks)...")
dataset = load_dataset('csv', data_files='ai_vs_human_dataset.csv', split='train')

print("[2/4] Tokenizing and formatting semantic language matrix...")
tokenizer = AutoTokenizer.from_pretrained("roberta-base")

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

tokenized_datasets = dataset.map(tokenize_function, batched=True)
split_dataset = tokenized_datasets.train_test_split(test_size=0.1, seed=42)

print("[3/4] Loading RoBERTa Neural Network into GPU VRAM...")
model = AutoModelForSequenceClassification.from_pretrained("roberta-base", num_labels=2)

training_args = TrainingArguments(
    output_dir="./text_ai_results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_steps=50,
    fp16=True, 
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

print("\n[4/4] Saving upgraded Text Model to disk...")
trainer.save_model("model_text_finetuned")
tokenizer.save_pretrained("model_text_finetuned")
print("\nTEXT AI UPGRADE 100% COMPLETE!")

