import torch
import torch.nn as nn
from torchvision import transforms
from transformers import ViTModel
from PIL import Image
class DeepfakeViT(nn.Module):
    def __init__(self):
        super().__init__()
        self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
        self.classifier = nn.Sequential(nn.Linear(self.vit.config.hidden_size, 256), nn.ReLU(), nn.Dropout(0.3), nn.Linear(256, 1))
    def forward(self, pixel_values):
        return self.classifier(self.vit(pixel_values=pixel_values).pooler_output)

device = torch.device('cpu')
model = DeepfakeViT().to(device)
model.load_state_dict(torch.load('D:/voice-check/voice-check/model_image_vit_best.pth', map_location=device))
model.eval()

img = Image.open('D:/voice-check/voice-check/dataset_image/fake/complex_ai_214979.jpg').convert('RGB')
img = img.resize((224, 224))
transform = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(), transforms.Normalize([0.5]*3, [0.5]*3)])

with torch.no_grad():
    logits = model(transform(img).unsqueeze(0).to(device))
    print(float(torch.sigmoid(logits).cpu().item()))
