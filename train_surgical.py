import torch
import torch.nn as nn
from torchvision import transforms
from transformers import ViTModel
from PIL import Image
import torch.optim as optim
import os

print("--- SURGICAL FINE-TUNING ---")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

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

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])

# Micro-dataset
data = [
    # FAKE IMAGES (Label 0.0)
    ('C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787396274505.jpg', 0.0),
    ('C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787399134182.png', 0.0),
    # REAL IMAGES (Label 1.0)
    ('C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787398581135.png', 1.0)
]

for epoch in range(25):
    total_loss = 0
    for img_path, label in data:
        img = Image.open(img_path).convert('RGB')
        img_t = transform(img).unsqueeze(0).to(device)
        target = torch.tensor([[label]]).to(device)
        
        optimizer.zero_grad()
        out = model(img_t)
        loss = criterion(out, target)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch+1}/25 - Loss: {total_loss:.4f}")

torch.save(model.state_dict(), model_path)
print("Surgical fine-tuning complete. Model saved.")
