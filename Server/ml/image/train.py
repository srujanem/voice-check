"""
Training Script — PixelGuard (Image AI vs Human Detection)
Optimized for RTX 4050 6GB with mixed precision training

Usage:
  python -m ml.image.train

Data structure expected:
  data/
    images/
      human/   ← .jpg, .png, .webp real photos
      ai/      ← .jpg, .png AI-generated images
"""
import sys
import json
import time
from pathlib import Path
from datetime import datetime

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader, Dataset, random_split
from torch.cuda.amp import GradScaler, autocast
from torchvision import transforms
from PIL import Image
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from ml.image.model import PixelGuardModel


# =================== AUGMENTATION ===================
TRAIN_TRANSFORMS = transforms.Compose([
    transforms.Resize((400, 400)),
    transforms.RandomCrop(380),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.1),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1, hue=0.05),
    transforms.RandomGrayscale(p=0.05),
    transforms.RandomRotation(degrees=15),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    transforms.RandomErasing(p=0.1)
])

VAL_TRANSFORMS = transforms.Compose([
    transforms.Resize((380, 380)),
    transforms.CenterCrop(380),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


# =================== DATASET ===================
class ImageDataset(Dataset):
    """
    Loads images from data/images/human/ and data/images/ai/
    Labels: 0 = AI, 1 = Human
    """
    def __init__(self, data_dir: str, transform=None):
        self.transform = transform
        self.files = []
        self.labels = []

        data_path = Path(data_dir)
        extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

        for f in (data_path / "ai").glob("**/*"):
            if f.suffix.lower() in extensions:
                self.files.append(str(f))
                self.labels.append(0)

        for f in (data_path / "human").glob("**/*"):
            if f.suffix.lower() in extensions:
                self.files.append(str(f))
                self.labels.append(1)

        ai_count = sum(1 for l in self.labels if l == 0)
        human_count = sum(1 for l in self.labels if l == 1)
        print(f"📂 Dataset loaded: {ai_count} AI, {human_count} Human images")

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        try:
            img = Image.open(self.files[idx]).convert("RGB")
            if self.transform:
                img = self.transform(img)
            return img, torch.tensor(self.labels[idx], dtype=torch.long)
        except Exception as e:
            print(f"⚠️ Error loading {self.files[idx]}: {e}")
            blank = torch.zeros(3, 380, 380)
            return blank, torch.tensor(self.labels[idx], dtype=torch.long)


# =================== TRAINER ===================
class PixelGuardTrainer:
    def __init__(self, config: dict):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.scaler = GradScaler(enabled=config.get("mixed_precision", True) and self.device.type == "cuda")

        print(f"\n{'='*60}")
        print(f"  🖼️  PIXELGUARD TRAINING")
        print(f"{'='*60}")
        print(f"  Device: {self.device}")
        if self.device.type == "cuda":
            gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"  GPU: {torch.cuda.get_device_properties(0).name} ({gpu_mem:.1f}GB)")
        print(f"  Epochs: {config['epochs']}")
        print(f"  Batch Size: {config['batch_size']}")
        print(f"{'='*60}\n")

        self._setup_data()
        self._setup_model()
        self._setup_training()

    def _setup_data(self):
        full_dataset = ImageDataset(data_dir=self.config["data_dir"])
        if len(full_dataset) == 0:
            raise ValueError("❌ No images found! Please add files to data/images/human/ and data/images/ai/")

        val_size = int(len(full_dataset) * self.config.get("val_split", 0.2))
        train_size = len(full_dataset) - val_size
        train_idx, val_idx = random_split(range(len(full_dataset)), [train_size, val_size])

        class SubsetWithTransform(Dataset):
            def __init__(self, parent, indices, transform):
                self.parent = parent
                self.indices = indices
                self.transform = transform
            def __len__(self): return len(self.indices)
            def __getitem__(self, i):
                file_path = self.parent.files[self.indices[i]]
                label = self.parent.labels[self.indices[i]]
                try:
                    img = Image.open(file_path).convert("RGB")
                    return self.transform(img), torch.tensor(label, dtype=torch.long)
                except:
                    return torch.zeros(3, 380, 380), torch.tensor(label, dtype=torch.long)

        train_set = SubsetWithTransform(full_dataset, train_idx.indices, TRAIN_TRANSFORMS)
        val_set = SubsetWithTransform(full_dataset, val_idx.indices, VAL_TRANSFORMS)

        self.train_loader = DataLoader(
            train_set, batch_size=self.config["batch_size"],
            shuffle=True, num_workers=self.config.get("num_workers", 2),
            pin_memory=self.device.type == "cuda"
        )
        self.val_loader = DataLoader(
            val_set, batch_size=self.config["batch_size"] * 2,
            shuffle=False, num_workers=self.config.get("num_workers", 2),
            pin_memory=self.device.type == "cuda"
        )
        print(f"📊 Train: {len(train_set)}, Val: {len(val_set)}")

    def _setup_model(self):
        self.model = PixelGuardModel(
            num_labels=2,
            dropout=self.config.get("dropout", 0.3),
            use_frequency_module=self.config.get("use_fft", True)
        ).to(self.device)

        params = self.model.count_parameters()
        print(f"🧠 Model: {params['trainable']:,} trainable / {params['total']:,} total params")

    def _setup_training(self):
        self.optimizer = AdamW(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            lr=self.config["lr"], weight_decay=self.config.get("weight_decay", 0.01)
        )
        self.scheduler = CosineAnnealingLR(self.optimizer, T_max=self.config["epochs"])
        self.criterion = nn.CrossEntropyLoss(label_smoothing=0.05)
        self.best_val_acc = 0.0
        self.history = []

    def _epoch(self, loader, is_train: bool, epoch: int) -> dict:
        self.model.train() if is_train else self.model.eval()
        tag = "Train" if is_train else "Val  "
        total_loss, all_preds, all_labels = 0, [], []

        ctx = torch.enable_grad() if is_train else torch.no_grad()
        with ctx:
            for inputs, labels in tqdm(loader, desc=f"Epoch {epoch+1} [{tag}]", leave=False):
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                if is_train: self.optimizer.zero_grad()

                with autocast(device_type=self.device.type, enabled=self.config.get("mixed_precision", True)):
                    logits = self.model(inputs)
                    loss = self.criterion(logits, labels)

                if is_train:
                    self.scaler.scale(loss).backward()
                    self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    self.scaler.step(self.optimizer)
                    self.scaler.update()

                total_loss += loss.item()
                all_preds.extend(logits.argmax(dim=-1).cpu().numpy())
                all_labels.extend(labels.cpu().numpy())

        return {
            "loss": total_loss / len(loader),
            "accuracy": accuracy_score(all_labels, all_preds),
            "f1": f1_score(all_labels, all_preds, average="weighted", zero_division=0)
        }

    def train(self):
        print(f"🚀 Starting training for {self.config['epochs']} epochs...\n")
        start_time = time.time()

        for epoch in range(self.config["epochs"]):
            t0 = time.time()
            train_m = self._epoch(self.train_loader, True, epoch)
            val_m = self._epoch(self.val_loader, False, epoch)
            self.scheduler.step()

            is_best = val_m["accuracy"] > self.best_val_acc
            if is_best: self.best_val_acc = val_m["accuracy"]

            # Save checkpoint
            checkpoint = {
                "epoch": epoch, "model_state_dict": self.model.state_dict(),
                "val_accuracy": val_m["accuracy"], "val_f1": val_m["f1"],
                "version": "v1.0.0", "config": self.config,
                "trained_at": datetime.now().isoformat()
            }
            ckpt_dir = Path(self.config["checkpoint_dir"])
            ckpt_dir.mkdir(exist_ok=True)
            torch.save(checkpoint, ckpt_dir / "pixel_guard_latest.pt")
            if is_best:
                torch.save(checkpoint, ckpt_dir / "pixel_guard_best.pt")

            self.history.append({"epoch": epoch+1, "train": train_m, "val": val_m})
            print(f"Epoch {epoch+1:3d}/{self.config['epochs']} | "
                  f"Train Acc: {train_m['accuracy']:.4f} | "
                  f"Val Acc: {val_m['accuracy']:.4f} F1: {val_m['f1']:.4f} | "
                  f"{'⭐ BEST' if is_best else ''} [{time.time()-t0:.1f}s]")

        print(f"\n✅ Training done! Best val accuracy: {self.best_val_acc:.4f}")
        json.dump(self.history, open(Path(self.config["checkpoint_dir"]) / "pixel_guard_history.json", "w"), indent=2)
        return self.history


if __name__ == "__main__":
    config = {
        "data_dir": "./data/images",
        "checkpoint_dir": "./trained_models",
        "epochs": 20,
        "batch_size": 12,          # Conservative for 6GB VRAM with B4
        "lr": 1e-4,
        "weight_decay": 0.01,
        "dropout": 0.3,
        "val_split": 0.2,
        "use_fft": True,
        "num_workers": 2,
        "mixed_precision": True,
    }

    trainer = PixelGuardTrainer(config)
    history = trainer.train()
    print("\n🖼️ PixelGuard training complete!")
