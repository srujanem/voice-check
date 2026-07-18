"""
Training Script — VoiceShield (Audio AI vs Human Detection)
Optimized for RTX 4050 6GB with mixed precision training

Usage:
  python -m ml.audio.train

Data structure expected:
  data/
    audio/
      human/   ← .wav, .mp3 files of real human voice
      ai/      ← .wav, .mp3 files of AI-generated voice
"""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader, Dataset, random_split
from torch.cuda.amp import GradScaler, autocast
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, classification_report
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from ml.audio.model import VoiceShieldModel


# =================== DATASET ===================
class AudioDataset(Dataset):
    """
    Loads audio files from data/audio/human/ and data/audio/ai/
    Labels: 0 = AI, 1 = Human
    """
    def __init__(self, data_dir: str, max_duration_sec: float = 5.0, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.max_length = int(max_duration_sec * sample_rate)
        self.files = []
        self.labels = []

        data_path = Path(data_dir)
        ai_dir = data_path / "ai"
        human_dir = data_path / "human"

        extensions = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}

        for f in ai_dir.glob("**/*"):
            if f.suffix.lower() in extensions:
                self.files.append(str(f))
                self.labels.append(0)  # AI = 0

        for f in human_dir.glob("**/*"):
            if f.suffix.lower() in extensions:
                self.files.append(str(f))
                self.labels.append(1)  # Human = 1

        print(f"📂 Dataset loaded: {len([l for l in self.labels if l==0])} AI, "
              f"{len([l for l in self.labels if l==1])} Human samples")

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        import torchaudio
        audio_path = self.files[idx]
        label = self.labels[idx]

        try:
            waveform, sr = torchaudio.load(audio_path)
            if sr != self.sample_rate:
                resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
                waveform = resampler(waveform)

            # Convert to mono
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)

            waveform = waveform.squeeze(0)

            # Pad or truncate
            if len(waveform) > self.max_length:
                waveform = waveform[:self.max_length]
            else:
                pad_len = self.max_length - len(waveform)
                waveform = torch.nn.functional.pad(waveform, (0, pad_len))

            # Normalize
            waveform = waveform / (waveform.abs().max() + 1e-8)

            return waveform, torch.tensor(label, dtype=torch.long)

        except Exception as e:
            print(f"⚠️ Error loading {audio_path}: {e}")
            return torch.zeros(self.max_length), torch.tensor(label, dtype=torch.long)


# =================== TRAINER ===================
class VoiceShieldTrainer:
    def __init__(self, config: dict):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.scaler = GradScaler(enabled=config.get("mixed_precision", True) and self.device.type == "cuda")

        print(f"\n{'='*60}")
        print(f"  🎙️  VOICESHIELD TRAINING")
        print(f"{'='*60}")
        print(f"  Device: {self.device}")
        if self.device.type == "cuda":
            gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"  GPU: {torch.cuda.get_device_properties(0).name} ({gpu_mem:.1f}GB)")
        print(f"  Epochs: {config['epochs']}")
        print(f"  Batch Size: {config['batch_size']}")
        print(f"  Learning Rate: {config['lr']}")
        print(f"  Mixed Precision: {config.get('mixed_precision', True)}")
        print(f"{'='*60}\n")

        self._setup_data()
        self._setup_model()
        self._setup_training()

    def _setup_data(self):
        dataset = AudioDataset(
            data_dir=self.config["data_dir"],
            max_duration_sec=self.config.get("max_duration_sec", 5.0)
        )
        if len(dataset) == 0:
            raise ValueError("❌ No audio files found! Please add files to data/audio/human/ and data/audio/ai/")

        val_size = int(len(dataset) * self.config.get("val_split", 0.2))
        train_size = len(dataset) - val_size
        self.train_dataset, self.val_dataset = random_split(dataset, [train_size, val_size])

        self.train_loader = DataLoader(
            self.train_dataset,
            batch_size=self.config["batch_size"],
            shuffle=True,
            num_workers=self.config.get("num_workers", 2),
            pin_memory=self.device.type == "cuda"
        )
        self.val_loader = DataLoader(
            self.val_dataset,
            batch_size=self.config["batch_size"] * 2,
            shuffle=False,
            num_workers=self.config.get("num_workers", 2),
            pin_memory=self.device.type == "cuda"
        )
        print(f"📊 Train: {len(self.train_dataset)}, Val: {len(self.val_dataset)}")

    def _setup_model(self):
        self.model = VoiceShieldModel(
            num_labels=2,
            dropout=self.config.get("dropout", 0.3)
        ).to(self.device)

        params = self.model.count_parameters()
        print(f"🧠 Model: {params['trainable']:,} trainable / {params['total']:,} total params")

    def _setup_training(self):
        self.optimizer = AdamW(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            lr=self.config["lr"],
            weight_decay=self.config.get("weight_decay", 0.01)
        )
        self.scheduler = CosineAnnealingLR(
            self.optimizer,
            T_max=self.config["epochs"],
            eta_min=self.config["lr"] * 0.01
        )
        self.criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
        self.best_val_acc = 0.0
        self.history = []

    def _train_epoch(self, epoch: int) -> dict:
        self.model.train()
        total_loss = 0
        all_preds, all_labels = [], []

        pbar = tqdm(self.train_loader, desc=f"Epoch {epoch+1} [Train]", leave=False)
        for batch_idx, (inputs, labels) in enumerate(pbar):
            inputs = inputs.to(self.device)
            labels = labels.to(self.device)

            self.optimizer.zero_grad()

            with autocast(device_type=self.device.type, enabled=self.config.get("mixed_precision", True)):
                logits = self.model(inputs)
                loss = self.criterion(logits, labels)

            self.scaler.scale(loss).backward()
            self.scaler.unscale_(self.optimizer)
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.scaler.step(self.optimizer)
            self.scaler.update()

            total_loss += loss.item()
            preds = logits.argmax(dim=-1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.cpu().numpy())

            pbar.set_postfix(loss=f"{loss.item():.4f}")

        avg_loss = total_loss / len(self.train_loader)
        acc = accuracy_score(all_labels, all_preds)
        f1 = f1_score(all_labels, all_preds, average="weighted", zero_division=0)
        return {"loss": avg_loss, "accuracy": acc, "f1": f1}

    @torch.no_grad()
    def _val_epoch(self, epoch: int) -> dict:
        self.model.eval()
        total_loss = 0
        all_preds, all_labels = [], []

        for inputs, labels in tqdm(self.val_loader, desc=f"Epoch {epoch+1} [Val]  ", leave=False):
            inputs = inputs.to(self.device)
            labels = labels.to(self.device)

            with autocast(device_type=self.device.type, enabled=self.config.get("mixed_precision", True)):
                logits = self.model(inputs)
                loss = self.criterion(logits, labels)

            total_loss += loss.item()
            preds = logits.argmax(dim=-1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.cpu().numpy())

        avg_loss = total_loss / len(self.val_loader)
        acc = accuracy_score(all_labels, all_preds)
        f1 = f1_score(all_labels, all_preds, average="weighted", zero_division=0)
        return {"loss": avg_loss, "accuracy": acc, "f1": f1}

    def _save_checkpoint(self, epoch: int, val_metrics: dict, is_best: bool):
        checkpoint_dir = Path(self.config["checkpoint_dir"])
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "val_accuracy": val_metrics["accuracy"],
            "val_f1": val_metrics["f1"],
            "version": "v1.0.0",
            "config": self.config,
            "trained_at": datetime.now().isoformat()
        }

        # Save latest
        torch.save(checkpoint, checkpoint_dir / "voice_shield_latest.pt")

        # Save best
        if is_best:
            torch.save(checkpoint, checkpoint_dir / "voice_shield_best.pt")
            print(f"  💾 New best model saved! Acc: {val_metrics['accuracy']:.4f}")

    def train(self):
        print(f"🚀 Starting training for {self.config['epochs']} epochs...\n")
        start_time = time.time()

        for epoch in range(self.config["epochs"]):
            epoch_start = time.time()

            train_metrics = self._train_epoch(epoch)
            val_metrics = self._val_epoch(epoch)

            self.scheduler.step()
            epoch_time = time.time() - epoch_start

            is_best = val_metrics["accuracy"] > self.best_val_acc
            if is_best:
                self.best_val_acc = val_metrics["accuracy"]

            self._save_checkpoint(epoch, val_metrics, is_best)

            epoch_data = {
                "epoch": epoch + 1,
                "train": train_metrics,
                "val": val_metrics,
                "lr": self.optimizer.param_groups[0]["lr"],
                "time_sec": epoch_time
            }
            self.history.append(epoch_data)

            # Print progress
            print(f"Epoch {epoch+1:3d}/{self.config['epochs']} | "
                  f"Train Loss: {train_metrics['loss']:.4f} Acc: {train_metrics['accuracy']:.4f} | "
                  f"Val Loss: {val_metrics['loss']:.4f} Acc: {val_metrics['accuracy']:.4f} F1: {val_metrics['f1']:.4f} | "
                  f"{'⭐ BEST' if is_best else ''} "
                  f"[{epoch_time:.1f}s]")

        total_time = time.time() - start_time
        print(f"\n✅ Training complete in {total_time/60:.1f} minutes")
        print(f"🏆 Best validation accuracy: {self.best_val_acc:.4f}")

        # Save history
        history_path = Path(self.config["checkpoint_dir"]) / "voice_shield_history.json"
        with open(history_path, "w") as f:
            json.dump(self.history, f, indent=2)
        print(f"📈 Training history saved to {history_path}")

        return self.history


# =================== MAIN ===================
if __name__ == "__main__":
    config = {
        "data_dir": "./data/audio",
        "checkpoint_dir": "./trained_models",
        "epochs": 20,
        "batch_size": 8,           # Conservative for 6GB VRAM
        "lr": 1e-4,
        "weight_decay": 0.01,
        "dropout": 0.3,
        "val_split": 0.2,
        "max_duration_sec": 5.0,   # Clip audio to 5 seconds
        "num_workers": 2,
        "mixed_precision": True,
    }

    trainer = VoiceShieldTrainer(config)
    history = trainer.train()
    print("\n🎙️ VoiceShield training complete!")
