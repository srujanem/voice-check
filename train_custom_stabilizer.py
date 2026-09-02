import os
import glob
import torch
import torch.nn as nn
from torchvision import transforms
from transformers import ViTModel
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import sys

print("Starting script...", flush=True)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}", flush=True)

class CustomDataset(Dataset):
    def __init__(self, data_list, transform=None):
        self.data_list = data_list
        self.transform = transform
    def __len__(self): return len(self.data_list)
    def __getitem__(self, idx):
        img_path, label = self.data_list[idx]
        try:
            img = Image.open(img_path).convert('RGB')
            if self.transform: img = self.transform(img)
            return img, torch.tensor([label])
        except Exception as e:
            print(f"Error loading {img_path}: {e}", flush=True)
            # return a dummy tensor of correct shape to prevent crash
            dummy_img = torch.zeros(3, 224, 224)
            return dummy_img, torch.tensor([label])

data = []
for f in glob.glob('D:/voice-check/voice-check/dataset_custom/real/*.jpg'): data.append((f, 1.0))
for f in glob.glob('D:/voice-check/voice-check/dataset_custom/fake/*.jpg'): data.append((f, 0.0))

print(f"Found {len(data)} images in folders.", flush=True)

data.append(('C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787396274505.jpg', 0.0))
data.append(('C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787399134182.png', 0.0))
data.append(('C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787398581135.png', 1.0))

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.1, contrast=0.1),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])

dataset = CustomDataset(data, transform)
loader = DataLoader(dataset, batch_size=16, shuffle=True)

class DeepfakeViT(nn.Module):
    def __init__(self):
        super().__init__()
        self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
        self.classifier = nn.Sequential(nn.Linear(self.vit.config.hidden_size, 256), nn.ReLU(), nn.Dropout(0.3), nn.Linear(256, 1))
    def forward(self, pixel_values):
        return self.classifier(self.vit(pixel_values=pixel_values).pooler_output)

print("Loading model...", flush=True)
model = DeepfakeViT().to(device)
model_path = 'D:/voice-check/voice-check/model_image_vit_best.pth'
if os.path.exists(model_path):
    model.load_state_dict(torch.load(model_path, map_location=device))

model.train()
optimizer = torch.optim.Adam(model.parameters(), lr=3e-5) 
criterion = nn.BCEWithLogitsLoss()

print(f"Training on {len(data)} images to restore broad accuracy...", flush=True)
for epoch in range(5): # Reduced to 5 epochs since dataset is larger and we just want to inject the new real images
    total_loss = 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device).float()
        optimizer.zero_grad()
        out = model(imgs)
        loss = criterion(out, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch+1}/5 - Avg Loss: {total_loss/len(loader):.4f}", flush=True)

torch.save(model.state_dict(), model_path)
print("Model stabilized and saved.", flush=True)
