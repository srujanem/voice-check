import os
import torch
import torch.nn as nn
from torchvision import transforms
from transformers import ViTModel
from PIL import Image
import torch.optim as optim
from datasets import load_dataset
import numpy as np

print("=======================================================")
print("  AUTHGUARD: MASSIVE IMAGE AI DEEP LEARNING (OPTION 1)")
print("  - Engine: PyTorch Vision Transformer (ViT-Base)")
print("  - Dataset: 10,000+ Real vs AI (Midjourney/DALL-E)")
print("=======================================================")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

class DeepfakeViT(nn.Module):
    def __init__(self):
        super().__init__()
        self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
        self.classifier = nn.Sequential(nn.Linear(self.vit.config.hidden_size, 256), nn.ReLU(), nn.Dropout(0.3), nn.Linear(256, 1))
    def forward(self, pixel_values):
        return self.classifier(self.vit(pixel_values=pixel_values).pooler_output)

model = DeepfakeViT().to(device)
model_path = 'D:/voice-check/voice-check/model_image_vit_best.pth'
if os.path.exists(model_path):
    model.load_state_dict(torch.load(model_path, map_location=device))

model.train()
optimizer = optim.Adam(model.parameters(), lr=1e-5)
criterion = nn.BCEWithLogitsLoss()

print("\n[1/3] Streaming massive dataset from HuggingFace (Hemg/AI-Generated-vs-Real-Images-Datasets)...")
# Load dataset in streaming mode to save disk space
dataset = load_dataset('Hemg/AI-Generated-vs-Real-Images-Datasets', split='train', streaming=True)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.1, contrast=0.1),
    transforms.ToTensor(), 
    transforms.Normalize([0.5]*3, [0.5]*3)
])

print("\n[2/3] Initiating massive training loop (10,000 images)...")
MAX_IMAGES = 10000
batch_size = 16
images_batch = []
targets_batch = []
count = 0
total_loss = 0

for idx, item in enumerate(dataset):
    if count >= MAX_IMAGES:
        break
        
    try:
        img = item['image'].convert('RGB')
        label = item['label'] # 'AiArtData' is 0, 'RealArt' is 1
        # If 'AiArtData', label is 0 (Fake). If 'RealArt', label is 1 (Real)
        target = float(label)
        
        images_batch.append(transform(img))
        targets_batch.append([target])
        
        if len(images_batch) == batch_size:
            batch_tensors = torch.stack(images_batch).to(device)
            batch_targets = torch.tensor(targets_batch).to(device)
            
            optimizer.zero_grad()
            outputs = model(batch_tensors)
            loss = criterion(outputs, batch_targets)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            images_batch = []
            targets_batch = []
            count += batch_size
            
            if count % 160 == 0:
                print(f"Processed {count}/{MAX_IMAGES} images | Current Avg Loss: {total_loss / 10:.4f}")
                total_loss = 0
                
    except Exception as e:
        pass

print("\n[3/3] Saving massive deepfake model...")
torch.save(model.state_dict(), model_path)
print("Model fine-tuned and saved successfully!")
print("ALL TASKS COMPLETED!")
