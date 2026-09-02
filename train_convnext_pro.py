import os
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import timm

print("\n=======================================================")
print("  AUTHGUARD PRO: CONVNEXT-V2 FORENSIC ENGINE")
print("  - Architecture: ConvNeXt-V2 (Base)")
print("  - Target: Micro-Pixel & Frequency Artifact Detection")
print("  - Resolution: 256x256 High-Fidelity")
print("=======================================================\n")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[1/5] Hardware Verified: {device.type.upper()}")

# 1. Advanced High-Res Transforms
IMG_SIZE = 256 # Higher resolution for better noise detection

train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    # Adding slight perspective warping to force the model to learn deep structural features
    transforms.RandomPerspective(distortion_scale=0.1, p=0.2), 
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print("[2/5] Hooking into dataset_image...")
dataset = datasets.ImageFolder("dataset_image", transform=train_transform)

# Class balancing for imbalanced datasets
class_counts = [0, 0]
for _, label in dataset.samples: 
    class_counts[label] += 1
    
weights = [1.0 / count if count > 0 else 0 for count in class_counts]
sample_weights = [weights[label] for _, label in dataset.samples]
sampler = torch.utils.data.WeightedRandomSampler(sample_weights, len(sample_weights))

dataloader = DataLoader(dataset, batch_size=16, sampler=sampler, num_workers=0, pin_memory=True)

print("[3/5] Downloading & Initializing ConvNeXt-V2 Base...")
class ConvNextPro(nn.Module):
    def __init__(self):
        super().__init__()
        # Pretrained on ImageNet-22k, fine-tuned on 1k, using masked autoencoder weights
        self.backbone = timm.create_model('convnextv2_base.fcmae_ft_in22k_in1k', pretrained=True, num_classes=0)
        self.classifier = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(self.backbone.num_features, 256),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(256, 1)
        )
        
    def forward(self, x):
        features = self.backbone(x)
        return self.classifier(features)

model = ConvNextPro().to(device)

optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.05)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=5)
criterion = nn.BCEWithLogitsLoss()
scaler = torch.amp.GradScaler('cuda') if torch.cuda.is_available() else None

print("[4/5] Starting High-Fidelity Training Loop...")
EPOCHS = 5
for epoch in range(1, EPOCHS + 1):
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    start_time = time.time()
    
    for i, (images, labels) in enumerate(dataloader):
        images, labels = images.to(device), labels.to(device).float().unsqueeze(1)
        optimizer.zero_grad()
        
        if scaler:
            with torch.amp.autocast('cuda'):
                outputs = model(images)
                loss = criterion(outputs, labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
        running_loss += loss.item()
        preds = (torch.sigmoid(outputs) > 0.5).float()
        correct += (preds == labels).sum().item()
        total += labels.size(0)
        
        if i % 10 == 0 and i > 0:
            print(f"   Batch {i}/{len(dataloader)} | Loss: {loss.item():.4f}")
            
    scheduler.step()
    epoch_acc = 100. * correct / total
    print(f"[*] Epoch {epoch}/{EPOCHS} | Acc: {epoch_acc:.2f}% | Time: {time.time()-start_time:.1f}s")

print("[5/5] Saving Professional Model...")
torch.save(model.state_dict(), "model_image_convnext_pro.pth")
print("\nSUCCESS: Model saved to 'model_image_convnext_pro.pth'")
