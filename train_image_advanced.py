import os
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models, regularizers
from sklearn.model_selection import train_test_split
import numpy as np
import shutil

BASE_DIR = 'dataset_image'
HUMAN_DIR = os.path.join(BASE_DIR, 'real')
AI_DIR = os.path.join(BASE_DIR, 'fake')

# 1. Custom Data Augmentation with JPEG Artifacts
def custom_augmentation(image):
    # Randomly apply JPEG compression artifacts (helps detect AI vs Human in the wild)
    if tf.random.uniform(()) > 0.5:
        quality = tf.random.uniform((), minval=40, maxval=90, dtype=tf.int32)
        # Cast to uint8, compress, cast back
        image = tf.cast(image, tf.uint8)
        image = tf.image.adjust_jpeg_quality(image, quality)
        image = tf.cast(image, tf.float32)
    return image

# 2. Prepare 70/15/15 Split Data Pipeline
# To do a perfect 70/15/15 split, we will use tf.data API
batch_size = 16
img_size = (224, 224)

print("Loading dataset and splitting 70/15/15...")
full_dataset = tf.keras.utils.image_dataset_from_directory(
    BASE_DIR,
    image_size=img_size,
    batch_size=batch_size,
    shuffle=True,
    seed=42
)

# Calculate split sizes based on batches
total_batches = len(full_dataset)
train_size = int(0.7 * total_batches)
val_size = int(0.15 * total_batches)

train_ds = full_dataset.take(train_size)
test_val_ds = full_dataset.skip(train_size)
val_ds = test_val_ds.take(val_size)
test_ds = test_val_ds.skip(val_size)

# Apply Augmentation ONLY to training data
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
    layers.RandomContrast(0.1)
])

def prepare(ds, augment=False):
    if augment:
        # Wrap the custom jpeg augmentation in a tf.py_function or map
        def apply_custom(x, y):
            x = tf.map_fn(custom_augmentation, x)
            return x, y
        ds = ds.map(apply_custom, num_parallel_calls=tf.data.AUTOTUNE)
        ds = ds.map(lambda x, y: (data_augmentation(x, training=True), y), num_parallel_calls=tf.data.AUTOTUNE)
    return ds.prefetch(buffer_size=tf.data.AUTOTUNE)

train_ds = prepare(train_ds, augment=True)
val_ds = prepare(val_ds)
test_ds = prepare(test_ds)

# 3. Transfer Learning Pipeline (EfficientNetB0)
print("Building Transfer Learning Model (EfficientNetB0)...")
base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Freeze the base model
base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.5),
    layers.Dense(256, activation='relu', kernel_regularizer=regularizers.l2(0.01)),
    layers.Dropout(0.3),
    layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print("Training Classifier Head...")
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=3
)

# Unfreeze top layers for fine-tuning
print("Unfreezing top 20 layers for Fine-Tuning...")
base_model.trainable = True
for layer in base_model.layers[:-20]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5), # Lower learning rate for fine-tuning
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print("Fine-tuning model...")
history_fine = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=3
)

# 4. Evaluate on 15% Test Set (Unseen Data)
print("\n--- FINAL TEST SET EVALUATION ---")
test_loss, test_acc = model.evaluate(test_ds)
print(f"Test Accuracy on strictly unseen data: {test_acc*100:.2f}%")

model.save('model_image_advanced.keras')
print("Model saved to model_image_advanced.keras")


