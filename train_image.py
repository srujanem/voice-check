import os
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping

DATASET_DIR = "dataset_image"
BALANCED_DIR = "dataset_image_balanced"
BATCH_SIZE = 16
IMG_SIZE = (224, 224) # Standard size for EfficientNet

# Ensure directories exist
os.makedirs(os.path.join(DATASET_DIR, "real"), exist_ok=True)
os.makedirs(os.path.join(DATASET_DIR, "fake"), exist_ok=True)

import shutil

# Count original images
original_real_files = os.listdir(os.path.join(DATASET_DIR, "real"))
original_fake_files = os.listdir(os.path.join(DATASET_DIR, "fake"))

real_count = len(original_real_files)
fake_count = len(original_fake_files)
print(f"Found {real_count} real images and {fake_count} fake images.")

# Check if we already have a pre-built balanced dataset with more data
balanced_fake_count = 0
balanced_real_count = 0
if os.path.exists(os.path.join(BALANCED_DIR, "fake")):
    balanced_fake_count = len(os.listdir(os.path.join(BALANCED_DIR, "fake")))
if os.path.exists(os.path.join(BALANCED_DIR, "real")):
    balanced_real_count = len(os.listdir(os.path.join(BALANCED_DIR, "real")))

if balanced_fake_count >= 50 and balanced_real_count >= 50:
    print(f"Using pre-built balanced dataset: {balanced_real_count} real + {balanced_fake_count} fake")
    TRAINING_DIR = BALANCED_DIR
elif fake_count >= 2 and real_count >= 2:
    # Determine the balanced amount (minimum of the two)
    min_count = min(real_count, fake_count)
    print(f"Balancing dataset... Training on exactly {min_count} real and {min_count} fake images.")
    # Create clean balanced directory
    if os.path.exists(BALANCED_DIR):
        shutil.rmtree(BALANCED_DIR)
    os.makedirs(os.path.join(BALANCED_DIR, "real"), exist_ok=True)
    os.makedirs(os.path.join(BALANCED_DIR, "fake"), exist_ok=True)
    
    # Copy exactly `min_count` images to the balanced directory
    for f in original_real_files[:min_count]:
        shutil.copy2(os.path.join(DATASET_DIR, "real", f), os.path.join(BALANCED_DIR, "real", f))
    for f in original_fake_files[:min_count]:
        shutil.copy2(os.path.join(DATASET_DIR, "fake", f), os.path.join(BALANCED_DIR, "fake", f))
    
    # Switch the training directory to the balanced one
    TRAINING_DIR = BALANCED_DIR
else:
    TRAINING_DIR = DATASET_DIR


if real_count < 2 or fake_count < 2:
    print("Not enough images found in dataset_image/real or dataset_image/fake.")
    print("Please add at least a few images to each folder and run this script again.")
    print("Creating a mock model for now so the backend can run...")
    
    # Create a mock untrained model just so the backend doesn't crash
    base_model = EfficientNetB0(weights=None, include_top=False, input_shape=(224, 224, 3))
    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.save("model_image.keras")
    print("Mock model saved to 'model_image.keras'.")
    exit()

print("Loading dataset...")

# Load dataset using tf.keras utilities
train_dataset = tf.keras.utils.image_dataset_from_directory(
    TRAINING_DIR,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

val_dataset = tf.keras.utils.image_dataset_from_directory(
    TRAINING_DIR,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

# Optimize datasets for performance
AUTOTUNE = tf.data.AUTOTUNE
train_dataset = train_dataset.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_dataset = val_dataset.cache().prefetch(buffer_size=AUTOTUNE)

print("Building EfficientNet model...")

# Load pre-trained EfficientNet without the top classification layer
base_model = EfficientNetB0(input_shape=(224, 224, 3), include_top=False, weights='imagenet')

# Freeze the base model
base_model.trainable = False

# Build the complete model
model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    BatchNormalization(),
    Dropout(0.2),
    Dense(128, activation='relu'),
    BatchNormalization(),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

print("Starting training...")

model.fit(
    train_dataset,
    validation_data=val_dataset,
    epochs=20,
    callbacks=[early_stopping]
)

print("Fine-tuning the model...")
# Unfreeze top layers for fine-tuning
base_model.trainable = True
for layer in base_model.layers[:-20]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

model.fit(
    train_dataset,
    validation_data=val_dataset,
    epochs=10,
    callbacks=[early_stopping]
)

model.save("model_image.keras")
print("Training complete! Model saved to 'model_image.keras'.")
print("You can now start your backend with `python app.py`.")
