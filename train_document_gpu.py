import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
import time

print("==================================================")
print("  INITIALIZING DOCUMENT FORGERY AI TRAINING")
print("==================================================")

# Configurations
DATA_DIR = "dataset_document"
MODEL_SAVE_PATH = os.path.join("models", "model_document_forgery.pth")
BATCH_SIZE = 16
EPOCHS = 5
IMG_SIZE = 224
LEARNING_RATE = 1e-4

# Check for GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using compute device: {device.type.upper()}")
if device.type == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Transformations (Resize, Convert to Tensor, Normalize)
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print("\nLoading dataset from disk...")
# Load dataset
# ImageFolder expects subdirectories to be the class names (real, fake)
full_dataset = datasets.ImageFolder(root=DATA_DIR, transform=transform)
print(f"Classes found: {full_dataset.classes}")
print(f"Total documents: {len(full_dataset)}")

# Split into Train (80%) and Validation (20%)
train_size = int(0.8 * len(full_dataset))
val_size = len(full_dataset) - train_size
train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

# Build Model: Using ResNet18 (Excellent for local pixel anomalies like ELA/Forgery)
print("\nLoading Pretrained ResNet18 architecture...")
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)

# Freeze early layers to retain generic edge detection
for param in list(model.parameters())[:-15]:
    param.requires_grad = False

# Replace the final fully connected layer for 2 classes (Real vs Fake)
num_ftrs = model.fc.in_features
model.fc = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(num_ftrs, 2)
)

model = model.to(device)

# Loss and Optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE)

print("\nStarting Training Loop...")
start_time = time.time()

for epoch in range(EPOCHS):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * inputs.size(0)
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
    epoch_loss = running_loss / len(train_dataset)
    epoch_acc = correct / total
    
    # Validation
    model.eval()
    val_loss = 0.0
    val_correct = 0
    val_total = 0
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            val_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs, 1)
            val_total += labels.size(0)
            val_correct += (predicted == labels).sum().item()
            
    val_epoch_loss = val_loss / len(val_dataset)
    val_epoch_acc = val_correct / val_total
    
    print(f"Epoch [{epoch+1}/{EPOCHS}] - Train Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f} | Val Loss: {val_epoch_loss:.4f} Acc: {val_epoch_acc:.4f}")

total_time = time.time() - start_time
print(f"\nTraining completed in {total_time/60:.2f} minutes!")

# Save the model
os.makedirs("models", exist_ok=True)
torch.save(model.state_dict(), MODEL_SAVE_PATH)
print(f"Model successfully saved to: {MODEL_SAVE_PATH}")
