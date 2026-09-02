import os
import tensorflow as tf
from PIL import Image
import numpy as np
import torch
from torchvision import transforms
from transformers import ViTModel
import torch.nn as nn

repo_dir = r"D:\voice-check\voice-check"
file_path = r"D:\voice-check\voice-check\dataset_image\real\0001749b15164e268d70a1e4c364fddc.jpg"

print("--- Testing TF Model ---")
tf_model_path = os.path.join(repo_dir, "model_image_best_grid.keras")
tf_model = tf.keras.models.load_model(tf_model_path)
print(f"TF Input shape: {tf_model.input_shape}")
input_shape = tf_model.input_shape
img_h = input_shape[1] if input_shape[1] else 150
img_w = input_shape[2] if input_shape[2] else 150

img = Image.open(file_path).convert('RGB')
img_tf = img.resize((img_w, img_h))
img_array = np.array(img_tf) / 255.0
img_array = np.expand_dims(img_array, axis=0)
tf_prediction = float(tf_model.predict(img_array, verbose=0)[0][0])
print(f"TF Prediction (0=Real, 1=AI): {tf_prediction}")

print("--- Testing ViT Model ---")
vit_model_path = os.path.join(repo_dir, "model_image_vit_best.pth")
class DeepfakeViT(nn.Module):
    def __init__(self):
        super().__init__()
        self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
        self.classifier = nn.Sequential(nn.Linear(self.vit.config.hidden_size, 256), nn.ReLU(), nn.Dropout(0.3), nn.Linear(256, 1))
    def forward(self, pixel_values):
        return self.classifier(self.vit(pixel_values=pixel_values).pooler_output)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
vit_model = DeepfakeViT().to(device)
vit_model.load_state_dict(torch.load(vit_model_path, map_location=device))
vit_model.eval()

transform = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(), transforms.Normalize([0.5]*3, [0.5]*3)])
with torch.no_grad():
    vit_logits = vit_model(transform(img).unsqueeze(0).to(device))
    vit_prediction = float(torch.sigmoid(vit_logits).cpu().item())
print(f"ViT Prediction (0=Real, 1=AI): {vit_prediction}")

final_prediction = (tf_prediction + vit_prediction) / 2.0
print(f"Final Combined Prediction: {final_prediction}")
