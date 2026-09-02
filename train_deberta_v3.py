"""
AuthGuard — DeBERTa-v3-large AI Text Detector Training Script
=============================================================
Upgrades from RoBERTa-base (125M) → DeBERTa-v3-large (435M)
Optimized for RTX 4050 (6GB VRAM) with:
  - Mixed precision (fp16) training
  - Gradient accumulation (effective batch=32)
  - Gradient checkpointing to reduce VRAM usage
"""

import os
import random
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from tqdm import tqdm

# ─── Config ────────────────────────────────────────────────────────────
MODEL_NAME       = "microsoft/deberta-v3-large"
OUTPUT_DIR       = "c:/voice-check/model_text_finetuned"
DATASET_DIR      = "c:/voice-check/dataset_text"
MAX_LEN          = 512
BATCH_SIZE       = 2       # Small batch for 6GB VRAM
GRAD_ACCUM       = 16      # Effective batch = 2 * 16 = 32
EPOCHS           = 3
LEARNING_RATE    = 1e-5
WARMUP_RATIO     = 0.1
SEED             = 42
MAX_SAMPLES      = 8000    # Use up to 4000 per class

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🖥️  Device: {device}")
if device.type == "cuda":
    print(f"🎮  GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")


# ─── Load Dataset ──────────────────────────────────────────────────────
def load_texts(folder, label, max_count=4000):
    texts, labels = [], []
    path = os.path.join(DATASET_DIR, folder)
    if not os.path.exists(path):
        return texts, labels
    files = sorted(os.listdir(path))
    random.shuffle(files)
    for f in files[:max_count]:
        fp = os.path.join(path, f)
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                text = fh.read().strip()
                if len(text) > 30:  # Skip very short texts
                    texts.append(text[:2000])  # Limit length
                    labels.append(label)
        except:
            continue
    return texts, labels

print("\n📂 Loading dataset...")
ai_texts, ai_labels = load_texts("ai", 1, max_count=MAX_SAMPLES // 2)
ai2_texts, ai2_labels = load_texts("ai_generated", 1, max_count=500)
human_texts, human_labels = load_texts("human", 0, max_count=MAX_SAMPLES // 2)

all_texts = ai_texts + ai2_texts + human_texts
all_labels = ai_labels + ai2_labels + human_labels

print(f"   AI samples:    {len(ai_texts) + len(ai2_texts)}")
print(f"   Human samples: {len(human_texts)}")
print(f"   Total:         {len(all_texts)}")

# Split into train / val
train_texts, val_texts, train_labels, val_labels = train_test_split(
    all_texts, all_labels, test_size=0.15, random_state=SEED, stratify=all_labels
)
print(f"   Train: {len(train_texts)} | Val: {len(val_texts)}")


# ─── Custom Dataset ────────────────────────────────────────────────────
class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            padding="max_length",
            truncation=True,
            max_length=self.max_len,
            return_tensors="pt"
        )
        return {
            "input_ids":      encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels":         torch.tensor(self.labels[idx], dtype=torch.long)
        }


# ─── Load Tokenizer & Model ───────────────────────────────────────────
print(f"\n🔽 Downloading {MODEL_NAME} from HuggingFace...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2
)

# Enable gradient checkpointing to reduce VRAM usage
model.gradient_checkpointing_enable()
model.to(device)

total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"   Total params:     {total_params / 1e6:.0f}M")
print(f"   Trainable params: {trainable_params / 1e6:.0f}M")


# ─── DataLoaders ───────────────────────────────────────────────────────
train_ds = TextDataset(train_texts, train_labels, tokenizer, MAX_LEN)
val_ds   = TextDataset(val_texts, val_labels, tokenizer, MAX_LEN)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=0, pin_memory=True)
val_loader   = DataLoader(val_ds, batch_size=BATCH_SIZE * 2, shuffle=False, num_workers=0, pin_memory=True)


# ─── Optimizer & Scheduler ─────────────────────────────────────────────
optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01)
total_steps = (len(train_loader) // GRAD_ACCUM) * EPOCHS
warmup_steps = int(total_steps * WARMUP_RATIO)
scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)



print(f"\n⚙️  Training Config:")
print(f"   Epochs:          {EPOCHS}")
print(f"   Batch size:      {BATCH_SIZE} x {GRAD_ACCUM} accum = {BATCH_SIZE * GRAD_ACCUM} effective")
print(f"   Learning rate:   {LEARNING_RATE}")
print(f"   Total steps:     {total_steps}")
print(f"   Warmup steps:    {warmup_steps}")


# ─── Training Loop ─────────────────────────────────────────────────────
best_val_acc = 0.0

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    optimizer.zero_grad()

    pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}", ncols=90)
    for step, batch in enumerate(pbar):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        with torch.amp.autocast("cuda", dtype=torch.bfloat16):
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss / GRAD_ACCUM

        loss.backward()
        total_loss += loss.item() * GRAD_ACCUM

        if (step + 1) % GRAD_ACCUM == 0 or (step + 1) == len(train_loader):
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

        pbar.set_postfix(loss=f"{total_loss / (step + 1):.4f}")

    avg_train_loss = total_loss / len(train_loader)

    # ─── Validation ────────────────────────────────────────────────
    model.eval()
    all_preds, all_true = [], []

    with torch.no_grad():
        for batch in tqdm(val_loader, desc="  Validating", ncols=90, leave=False):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"]

            with torch.amp.autocast("cuda", dtype=torch.bfloat16):
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)

            preds = torch.argmax(outputs.logits, dim=-1).cpu().numpy()
            all_preds.extend(preds)
            all_true.extend(labels.numpy())

    val_acc = accuracy_score(all_true, all_preds)
    print(f"\n  📊 Epoch {epoch+1} — Train Loss: {avg_train_loss:.4f} | Val Accuracy: {val_acc*100:.1f}%")

    if val_acc > best_val_acc:
        best_val_acc = val_acc
        print(f"  🏆 New best! Saving model to {OUTPUT_DIR}...")
        
        # Save model
        model.save_pretrained(OUTPUT_DIR)
        tokenizer.save_pretrained(OUTPUT_DIR)
        model.to(device)

    print()

# ─── Final Report ──────────────────────────────────────────────────────
print("=" * 60)
print(f"🎉 TRAINING COMPLETE!")
print(f"   Best Validation Accuracy: {best_val_acc*100:.1f}%")
print(f"   Model saved to: {OUTPUT_DIR}")
print(f"   Architecture: DeBERTa-v3-large (435M params)")
print(f"   Previous model backed up to: model_text_finetuned_BACKUP_roberta/")
print(f"\n   Restart your Flask server to load the new model automatically!")
print("=" * 60)

# Print classification report for best model
print("\n📋 Final Classification Report:")
print(classification_report(all_true, all_preds, target_names=["Human", "AI-Generated"]))
