# -*- coding: utf-8 -*-
import os, glob, shutil
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras import layers, models
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms
from transformers import ViTModel
from torch.utils.data import DataLoader, Dataset
from PIL import Image

print("==========================================================")
print("     AUTHGUARD AI - DUAL IMAGE MODEL TRAINING ENGINE      ")
print("==========================================================")

BASE_DIR = 'D:/voice-check/voice-check/dataset_image'
print(f"Dataset path: {BASE_DIR}")
real_imgs = glob.glob(os.path.join(BASE_DIR, 'real', '*'))
fake_imgs = glob.glob(os.path.join(BASE_DIR, 'fake', '*'))
print(f"Dataset statistics: {len(real_imgs)} Real images, {len(fake_imgs)} Fake images")

# ------------------------------------------------------------
# 1. TENSORFLOW EFFICIENTNET TRAINING
# ------------------------------------------------------------
print("\n[1/2] Training TensorFlow EfficientNet CNN...")
img_size = (224, 224)
batch_size = 32

full_dataset = tf.keras.utils.image_dataset_from_directory(
    BASE_DIR,
    image_size=img_size,
    batch_size=batch_size,
    shuffle=True,
    seed=42
)

# Extract labels for class weighting
labels = []
for images, class_labels in full_dataset.unbatch():
    labels.append(class_labels.numpy())
labels = np.array(labels)

class_weights_arr = compute_class_weight(class_weight='balanced', classes=np.unique(labels), y=labels)
class_weight_dict = {i: float(weight) for i, weight in enumerate(class_weights_arr)}
print("Class weights (balanced):", class_weight_dict)

total_batches = len(full_dataset)
train_size = int(0.85 * total_batches)
train_ds = full_dataset.take(train_size)
val_ds = full_dataset.skip(train_size)

data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.12),
    layers.RandomZoom(0.1),
    layers.RandomContrast(0.1)
])

train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y), num_parallel_calls=tf.data.AUTOTUNE)
train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

tf_model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.4),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(1, activation='sigmoid')
])

tf_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print("Training CNN Head (3 epochs)...")
tf_model.fit(train_ds, validation_data=val_ds, epochs=3, class_weight=class_weight_dict)

print("Fine-tuning CNN top layers (2 epochs)...")
base_model.trainable = True
for layer in base_model.layers[:-25]:
    layer.trainable = False

tf_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='binary_crossentropy',
    metrics=['accuracy']
)
tf_model.fit(train_ds, validation_data=val_ds, epochs=2, class_weight=class_weight_dict)

val_loss, val_acc = tf_model.evaluate(val_ds)
print(f"CNN Final Accuracy: {val_acc*100:.2f}%")

tf_model.save('D:/voice-check/voice-check/model_image_advanced.keras')
tf_model.save('D:/voice-check/voice-check/model_image_best_grid.keras')
if os.path.exists('C:/voice-check/model_image_advanced.keras'):
    tf_model.save('C:/voice-check/model_image_advanced.keras')
print("Saved model_image_advanced.keras successfully.")

# ------------------------------------------------------------
# 2. PYTORCH VISION TRANSFORMER (ViT) TRAINING
# ------------------------------------------------------------
print("\n[2/2] Training PyTorch Vision Transformer (ViT-B/16)...")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"ViT Training Device: {device}")

class ImageDataset(Dataset):
    def __init__(self, data_list, transform=None):
        self.data_list = data_list
        self.transform = transform
    def __len__(self): return len(self.data_list)
    def __getitem__(self, idx):
        img_path, label = self.data_list[idx]
        try:
            img = Image.open(img_path).convert('RGB')
            if self.transform: img = self.transform(img)
            return img, torch.tensor([label], dtype=torch.float32)
        except Exception:
            dummy = torch.zeros(3, 224, 224)
            return dummy, torch.tensor([label], dtype=torch.float32)

vit_data = []
import random
random.seed(42)
sampled_real = random.sample(real_imgs, min(600, len(real_imgs)))
sampled_fake = random.sample(fake_imgs, min(600, len(fake_imgs)))

for f in sampled_real: vit_data.append((f, 1.0))
for f in sampled_fake: vit_data.append((f, 0.0))

print(f"ViT Training dataset: {len(vit_data)} balanced samples ({len(sampled_real)} Real, {len(sampled_fake)} Fake)")

vit_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.1, contrast=0.1),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])

vit_ds = ImageDataset(vit_data, vit_transform)
vit_loader = DataLoader(vit_ds, batch_size=16, shuffle=True)

class DeepfakeViT(nn.Module):
    def __init__(self):
        super().__init__()
        self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
        self.classifier = nn.Sequential(
            nn.Linear(self.vit.config.hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 1)
        )
    def forward(self, pixel_values):
        return self.classifier(self.vit(pixel_values=pixel_values).pooler_output)

vit_net = DeepfakeViT().to(device)
vit_path = 'D:/voice-check/voice-check/model_image_vit_best.pth'
if os.path.exists(vit_path):
    try:
        vit_net.load_state_dict(torch.load(vit_path, map_location=device))
        print("Loaded existing ViT checkpoint for warm-start.")
    except: pass

vit_net.train()
vit_optimizer = torch.optim.Adam(vit_net.parameters(), lr=2e-5)
vit_criterion = nn.BCEWithLogitsLoss()

print("Training ViT for 3 epochs...")
for epoch in range(3):
    total_loss = 0
    for imgs, targets in vit_loader:
        imgs, targets = imgs.to(device), targets.to(device)
        vit_optimizer.zero_grad()
        preds = vit_net(imgs)
        loss = vit_criterion(preds, targets)
        loss.backward()
        vit_optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch+1}/3 - ViT Loss: {total_loss/len(vit_loader):.4f}")

torch.save(vit_net.state_dict(), vit_path)
if os.path.exists('C:/voice-check/model_image_vit_best.pth'):
    torch.save(vit_net.state_dict(), 'C:/voice-check/model_image_vit_best.pth')
print("ViT model saved to model_image_vit_best.pth.")

print("\n==========================================================")
print("        ALL IMAGE MODELS SUCCESSFULLY RETRAINED!          ")
print("==========================================================")
