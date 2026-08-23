import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import timm
import os
import time

def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Dataset Paths
    base_dir = r"c:\voice-check\dataset_image"
    train_dir = base_dir

    # Image Size and Batch Size
    IMG_SIZE = 224
    BATCH_SIZE = 16  # Safe for 6GB VRAM with AMP
    EPOCHS = 4       # Fast run for high accuracy

    # Robust Augmentations
    train_transforms = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
        transforms.RandomPerspective(distortion_scale=0.2, p=0.3),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    print("Loading dataset...")
    # DataLoader
    train_dataset = datasets.ImageFolder(root=train_dir, transform=train_transforms)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4, pin_memory=True)
    print(f"Loaded {len(train_dataset)} images across {len(train_dataset.classes)} classes.")

    # Model: ConvNeXt V2 Tiny (extremely powerful, fits nicely in 6GB)
    print("Loading ConvNeXt V2 Tiny...")
    model = timm.create_model('convnextv2_tiny.fcmae_ft_in22k_in1k', pretrained=True, num_classes=2)
    model = model.to(device)

    # Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-2)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
    
    # AMP Scaler for mixed precision
    scaler = torch.amp.GradScaler('cuda')

    # Training Loop
    best_loss = float('inf')
    model_path = r"c:\voice-check\model_image_convnext_best.pth"

    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        start_time = time.time()

        for i, (inputs, labels) in enumerate(train_loader):
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()

            with torch.amp.autocast('cuda'):
                outputs = model(inputs)
                loss = criterion(outputs, labels)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            if (i + 1) % 50 == 0:
                print(f"Epoch [{epoch+1}/{EPOCHS}], Step [{i+1}/{len(train_loader)}], Loss: {loss.item():.4f}, Acc: {100.*correct/total:.2f}%")

        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100. * correct / total
        print(f"--- Epoch {epoch+1} Summary: Loss: {epoch_loss:.4f}, Acc: {epoch_acc:.2f}%, Time: {time.time()-start_time:.1f}s ---")
        
        scheduler.step()

        if epoch_loss < best_loss:
            best_loss = epoch_loss
            print("=> Saving new best model...")
            torch.save(model.state_dict(), model_path)

    print(f"Training complete. Best model saved to {model_path}.")

if __name__ == '__main__':
    train()
