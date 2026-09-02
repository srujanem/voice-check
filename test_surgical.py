import torch
import torch.nn as nn
from torchvision import transforms
from transformers import ViTModel
from PIL import Image

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
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])

# FAKE Modi image
img_fake = Image.open('C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787396274505.jpg').convert('RGB')
with torch.no_grad():
    out_fake = float(torch.sigmoid(model(transform(img_fake).unsqueeze(0).to(device))).cpu().item())
print(f"Modi Image (Expect ~0.0): {out_fake:.4f}")

# REAL User image
img_real = Image.open('C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787398581135.png').convert('RGB')
with torch.no_grad():
    out_real = float(torch.sigmoid(model(transform(img_real).unsqueeze(0).to(device))).cpu().item())
print(f"Real Image (Expect ~1.0): {out_real:.4f}")

# SECOND FAKE Modi image
img_fake2 = Image.open('C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787399134182.png').convert('RGB')
with torch.no_grad():
    out_fake2 = float(torch.sigmoid(model(transform(img_fake2).unsqueeze(0).to(device))).cpu().item())
print(f"Modi Image 2 (Expect ~0.0): {out_fake2:.4f}")
