import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from transformers import ViTModel
import time
import logging

logging.disable(logging.WARNING)

print("\n=======================================================")
print("  AUTHGUARD: INITIATING VISION TRANSFORMER (ViT) ")
print("  - Target: Global Structural Deepfake Detection")
print("  - Engine: PyTorch + NVIDIA CUDA (GPU)")
print("=======================================================\n")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[1/5] Verified Hardware: {device.type.upper()}")

# 1. Data Preparation
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

print("[2/5] Hooking into image dataset: dataset_image...")
dataset = datasets.ImageFolder("dataset_image", transform=transform)

class_counts = [0, 0]
for _, label in dataset.samples:
    class_counts[label] += 1

weight = [1.0 / class_counts[0], 1.0 / class_counts[1]]
sample_weights = [weight[label] for _, label in dataset.samples]
sampler = torch.utils.data.WeightedRandomSampler(sample_weights, len(sample_weights))

dataloader = DataLoader(dataset, batch_size=32, sampler=sampler, num_workers=0, pin_memory=True)

# 2. Model Definition
print("[3/5] Downloading & Assembling Vision Transformer (ViT)...")
class DeepfakeViT(nn.Module):
    def __init__(self):
        super().__init__()
        self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
        self.classifier = nn.Sequential(
            nn.Linear(self.vit.config.hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 1)
            # Sigmoid removed for BCEWithLogitsLoss numerical stability
        )
        
    def forward(self, pixel_values):
        outputs = self.vit(pixel_values=pixel_values)
        sequence_output = outputs.pooler_output
        return self.classifier(sequence_output)

model = DeepfakeViT().to(device)

optimizer = optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
criterion = nn.BCEWithLogitsLoss()
scaler = torch.amp.GradScaler('cuda') 

print("[4/5] Initiating Dual-Engine PyTorch Training Loop...")

EPOCHS = 6
for epoch in range(1, EPOCHS + 1):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    start_time = time.time()
    
    for i, (images, labels) in enumerate(dataloader):
        images, labels = images.to(device), labels.to(device).float().unsqueeze(1)
        
        optimizer.zero_grad()
        
        with torch.amp.autocast('cuda'):
            outputs = model(images)
            loss = criterion(outputs, labels)
            
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        
        running_loss += loss.item()
        
        # With logits, > 0.0 is equivalent to probability > 0.5
        predicted = (outputs > 0.0).float()
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
        if (i + 1) % 50 == 0:
            print(f"   - Epoch {epoch} | Batch {i+1}/{len(dataloader)} | Batch Loss: {loss.item():.4f} | Batch Acc: {100*(predicted == labels).sum().item()/labels.size(0):.2f}%")

    epoch_acc = 100 * correct / total
    epoch_time = time.time() - start_time
    print(f"-> EPOCH {epoch} COMPLETE | Accuracy: {epoch_acc:.2f}% | Loss: {running_loss/len(dataloader):.4f} | Time: {epoch_time:.0f}s\n")

print("[5/5] Saving final Vision Transformer model...")
torch.save(model.state_dict(), "model_image_vit_best.pth")
print("\nVISION TRANSFORMER UPGRADE 100% COMPLETE!")
