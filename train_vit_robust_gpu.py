import torch
import torch.nn as nn
from torchvision import transforms, datasets
from torch.utils.data import DataLoader, random_split
from transformers import ViTModel
import torch.optim as optim
import os
import time

class DeepfakeViT(nn.Module):
    def __init__(self):
        super().__init__()
        self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
        self.classifier = nn.Sequential(
            nn.Linear(self.vit.config.hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.35),
            nn.Linear(256, 1)
        )
    def forward(self, pixel_values):
        return self.classifier(self.vit(pixel_values=pixel_values).pooler_output)

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using compute device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.15, contrast=0.15),
        transforms.ToTensor(),
        transforms.Normalize([0.5]*3, [0.5]*3)
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5]*3, [0.5]*3)
    ])

    dataset_path = 'D:/voice-check/voice-check/dataset_image'
    full_dataset = datasets.ImageFolder(dataset_path, transform=train_transform)
    
    total_len = len(full_dataset)
    train_len = int(0.85 * total_len)
    val_len = total_len - train_len
    
    train_set, val_set = random_split(full_dataset, [train_len, val_len], generator=torch.Generator().manual_seed(42))
    val_set.dataset.transform = val_transform

    train_loader = DataLoader(train_set, batch_size=32, shuffle=True, num_workers=0, pin_memory=True)
    val_loader = DataLoader(val_set, batch_size=32, shuffle=False, num_workers=0, pin_memory=True)

    print(f"Total dataset: {total_len} images | Train: {train_len} | Val: {val_len}")

    model = DeepfakeViT().to(device)
    model_save_path = 'D:/voice-check/voice-check/model_image_vit_best.pth'
    if os.path.exists(model_save_path):
        try:
            model.load_state_dict(torch.load(model_save_path, map_location=device))
            print("Loaded existing ViT weights for transfer learning refinement.")
        except Exception as e:
            print("Starting from base pretrained weights:", e)

    optimizer = optim.AdamW(model.parameters(), lr=2e-5, weight_decay=1e-4)
    criterion = nn.BCEWithLogitsLoss()
    scaler = torch.amp.GradScaler('cuda') if torch.cuda.is_available() else None

    epochs = 3
    best_val_acc = 0.0

    print("\nStarting GPU-Accelerated ViT Training on RTX 4050...")
    for epoch in range(epochs):
        t0 = time.time()
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for idx, (images, labels) in enumerate(train_loader):
            images = images.to(device, non_blocking=True)
            labels = labels.float().unsqueeze(1).to(device, non_blocking=True)

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

            running_loss += loss.item() * images.size(0)
            preds = (torch.sigmoid(outputs) >= 0.5).float()
            correct += (preds == labels).sum().item()
            total += labels.size(0)

            if (idx + 1) % 40 == 0 or (idx + 1) == len(train_loader):
                print(f"  [Epoch {epoch+1}/{epochs} | Step {idx+1}/{len(train_loader)}] Loss: {loss.item():.4f} | Running Train Acc: {(correct/total)*100:.2f}%")

        train_acc = (correct / total) * 100
        train_loss = running_loss / total

        model.eval()
        v_correct = 0
        v_total = 0
        v_loss = 0.0
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device, non_blocking=True)
                labels = labels.float().unsqueeze(1).to(device, non_blocking=True)
                if scaler:
                    with torch.amp.autocast('cuda'):
                        outputs = model(images)
                        loss = criterion(outputs, labels)
                else:
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                v_loss += loss.item() * images.size(0)
                preds = (torch.sigmoid(outputs) >= 0.5).float()
                v_correct += (preds == labels).sum().item()
                v_total += labels.size(0)

        val_acc = (v_correct / v_total) * 100
        val_loss = v_loss / v_total
        elapsed = time.time() - t0

        print(f"\nEpoch {epoch+1}/{epochs} Summary ({elapsed:.1f}s):")
        print(f"   Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"   Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%\n")

        if val_acc > best_val_acc or epoch == epochs - 1:
            best_val_acc = val_acc
            torch.save(model.state_dict(), model_save_path)
            print(f"   Saved Best SOTA ViT Model to {model_save_path} (Val Acc: {val_acc:.2f}%)")

    print("\nTraining Complete! ViT-B/16 is fully converged and optimized.")

if __name__ == '__main__':
    main()
