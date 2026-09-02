import tensorflow as tf
from PIL import Image
import numpy as np
import torch
from torchvision import transforms
from transformers import ViTModel
import torch.nn as nn

file_path = r"C:\Users\sruja\.gemini\antigravity\brain\14c6cba6-290a-4015-9068-c422a5c944fe\.user_uploaded\media_1787332074266.png"

tf_model = tf.keras.models.load_model(r"D:\voice-check\voice-check\model_image_advanced.keras")
img = Image.open(file_path).convert('RGB')
img_tf = img.resize((224, 224))
img_array = np.array(img_tf) / 255.0
img_array = np.expand_dims(img_array, axis=0)

tf_pred = float(tf_model.predict(img_array, verbose=0)[0][0])
print(f"TF Raw Prediction: {tf_pred}")

class DeepfakeViT(nn.Module):
    def __init__(self):
        super().__init__()
        self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
        self.classifier = nn.Sequential(nn.Linear(self.vit.config.hidden_size, 256), nn.ReLU(), nn.Dropout(0.3), nn.Linear(256, 1))
    def forward(self, pixel_values):
        return self.classifier(self.vit(pixel_values=pixel_values).pooler_output)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
vit_model = DeepfakeViT().to(device)
vit_model.load_state_dict(torch.load(r"D:\voice-check\voice-check\model_image_vit_best.pth", map_location=device, weights_only=True))
vit_model.eval()

transform = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(), transforms.Normalize([0.5]*3, [0.5]*3)])
with torch.no_grad():
    vit_logits = vit_model(transform(img).unsqueeze(0).to(device))
    vit_pred = float(torch.sigmoid(vit_logits).cpu().item())
print(f"ViT Raw Prediction: {vit_pred}")
