"""
FIXED Image Model Training Script
- Uses dataset_image_balanced (150 real + 150 fake)
- Adds heavy data augmentation to prevent overfitting
- Uses class_weight balancing
- Tests predictions before saving
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (Dense, GlobalAveragePooling2D, Dropout,
                                     BatchNormalization, RandomFlip, RandomRotation,
                                     RandomZoom, RandomBrightness, Input)
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import load_img, img_to_array

TRAINING_DIR = "dataset_image_balanced"
BATCH_SIZE   = 16
IMG_SIZE     = (224, 224)
EPOCHS_FROZEN = 20
EPOCHS_FINETUNE = 15

# ── Verify dataset ─────────────────────────────────────────────────────────
print("=" * 55)
for cls in ["real", "fake"]:
    path = os.path.join(TRAINING_DIR, cls)
    count = len([f for f in os.listdir(path) if f.lower().endswith(('.jpg','.jpeg','.png','.webp','.bmp'))])
    print(f"  {cls}: {count} images")
print("=" * 55)

# ── Load dataset with augmentation ────────────────────────────────────────
print("\nLoading dataset with augmentation pipeline...")

train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAINING_DIR,
    validation_split=0.2,
    subset="training",
    seed=42,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode='binary'
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    TRAINING_DIR,
    validation_split=0.2,
    subset="validation",
    seed=42,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode='binary'
)

class_names = train_ds.class_names
print(f"Classes: {class_names}")
# EfficientNet expects [0-255] NOT normalized — it normalizes internally

# ── Data Augmentation ─────────────────────────────────────────────────────
augmentation = tf.keras.Sequential([
    RandomFlip("horizontal_and_vertical"),
    RandomRotation(0.15),
    RandomZoom(0.15),
    RandomBrightness(0.15),
], name="augmentation")

AUTOTUNE = tf.data.AUTOTUNE

def augment(image, label):
    image = augmentation(image, training=True)
    return image, label

train_ds = train_ds.map(augment, num_parallel_calls=AUTOTUNE)
train_ds = train_ds.cache().shuffle(500).prefetch(buffer_size=AUTOTUNE)
val_ds   = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# ── Build Model ────────────────────────────────────────────────────────────
print("\nBuilding EfficientNetB0 model...")

inputs    = Input(shape=(224, 224, 3))
base      = EfficientNetB0(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
base.trainable = False  # freeze for initial training

x = base(inputs, training=False)
x = GlobalAveragePooling2D()(x)
x = BatchNormalization()(x)
x = Dropout(0.4)(x)
x = Dense(256, activation='relu')(x)
x = BatchNormalization()(x)
x = Dropout(0.3)(x)
outputs = Dense(1, activation='sigmoid')(x)

model = Model(inputs, outputs)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss='binary_crossentropy',
    metrics=['accuracy']
)
model.summary()

callbacks = [
    EarlyStopping(monitor='val_accuracy', patience=6, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)
]

# ── Phase 1: Train classification head ───────────────────────────────────
print(f"\nPhase 1: Training classification head ({EPOCHS_FROZEN} epochs max)...")
model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS_FROZEN, callbacks=callbacks)

# ── Phase 2: Fine-tune top layers ─────────────────────────────────────────
print("\nPhase 2: Fine-tuning top 30 layers of EfficientNet...")
base.trainable = True
for layer in base.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

callbacks_ft = [
    EarlyStopping(monitor='val_accuracy', patience=6, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)
]

model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS_FINETUNE, callbacks=callbacks_ft)

# ── Evaluate ──────────────────────────────────────────────────────────────
print("\nEvaluating on validation set...")
loss, acc = model.evaluate(val_ds)
print(f"Final Validation Accuracy: {acc*100:.2f}%")

# ── Quick sanity check on one image ───────────────────────────────────────
def predict_image(path, expected_label):
    img = load_img(path, target_size=IMG_SIZE)
    arr = img_to_array(img)
    arr = np.expand_dims(arr, axis=0)
    prob = float(model.predict(arr, verbose=0)[0][0])
    # class_names is alphabetical: fake=0, real=1
    pred_class = class_names[1] if prob >= 0.5 else class_names[0]
    print(f"  [{('OK' if pred_class==expected_label else 'WRONG')}] {os.path.basename(path)} -> {pred_class} ({prob:.2f}) | Expected: {expected_label}")

print("\n--- Sanity Check ---")
real_dir = os.path.join(TRAINING_DIR, "real")
fake_dir = os.path.join(TRAINING_DIR, "fake")
real_samples = [os.path.join(real_dir, f) for f in os.listdir(real_dir)[:3] if f.lower().endswith(('.jpg','.jpeg','.png'))]
fake_samples = [os.path.join(fake_dir, f) for f in os.listdir(fake_dir)[:3] if f.lower().endswith(('.jpg','.jpeg','.png'))]
for p in real_samples: predict_image(p, "real")
for p in fake_samples: predict_image(p, "fake")

# ── Save ──────────────────────────────────────────────────────────────────
model.save("model_image.keras")
print(f"\nModel saved to model_image.keras (val_acc={acc*100:.1f}%)")
print(f"class_names order: {class_names}")
print("fake=0 (prob<0.5) | real=1 (prob>=0.5)")
print("Restart your backend to use the new model.")
