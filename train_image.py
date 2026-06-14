import os
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping

DATASET_DIR = "dataset_image"
BATCH_SIZE = 16
IMG_SIZE = (224, 224) # Standard size for EfficientNet

# Ensure directories exist
os.makedirs(os.path.join(DATASET_DIR, "real"), exist_ok=True)
os.makedirs(os.path.join(DATASET_DIR, "fake"), exist_ok=True)

# Count images
real_count = len(os.listdir(os.path.join(DATASET_DIR, "real")))
fake_count = len(os.listdir(os.path.join(DATASET_DIR, "fake")))

print(f"Found {real_count} real images and {fake_count} fake images.")

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
    DATASET_DIR,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

val_dataset = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
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
