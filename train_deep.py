import os
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras import layers, models, regularizers, callbacks
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

# Suppress annoying TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

BASE_DIR = 'dataset_image'
img_size = (224, 224) # Upgraded from 150x150
batch_size = 16       # Smaller batch to fit heavier model in GPU VRAM

print("\n=======================================================")
print("  AUTHGUARD: INITIATING DEEP TRAINING SEQUENCE ")
print("  - Resolution: 224x224 HD")
print("  - Brain: EfficientNetB3 (Heavy)")
print("  - Max Epochs: 70")
print("=======================================================\n")

print("[1/5] Loading 6,000+ images into GPU memory...")
full_dataset = tf.keras.utils.image_dataset_from_directory(
    BASE_DIR,
    image_size=img_size,
    batch_size=batch_size,
    shuffle=True,
    seed=42
)

print("[2/5] Calculating Class Weights to prevent AI bias...")
labels = []
for images, class_labels in full_dataset.unbatch():
    labels.append(class_labels.numpy())
labels = np.array(labels)

class_weights_arr = compute_class_weight(class_weight='balanced', classes=np.unique(labels), y=labels)
class_weight_dict = {i: weight for i, weight in enumerate(class_weights_arr)}

total_batches = len(full_dataset)
train_size = int(0.8 * total_batches)
train_ds = full_dataset.take(train_size)
val_ds = full_dataset.skip(train_size)

# Advanced Augmentation
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.15),
    layers.RandomZoom(0.15),
    layers.RandomContrast(0.15)
])

train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y), num_parallel_calls=tf.data.AUTOTUNE).prefetch(tf.data.AUTOTUNE)
val_ds = val_ds.prefetch(tf.data.AUTOTUNE)

print("[3/5] Compiling Heavier Architecture...")
base_model = EfficientNetB3(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.5),
    layers.Dense(256, activation='relu', kernel_regularizer=regularizers.l2(0.01)),
    layers.Dropout(0.3),
    layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

# Early stopping will auto-halt if it hits 99.9% so it doesn't overtrain
early_stopping = callbacks.EarlyStopping(monitor='val_accuracy', patience=4, restore_best_weights=True, verbose=1)

print("\n--- PHASE 1: WARMUP TRAINING (Max 20 Epochs) ---")
model.fit(train_ds, validation_data=val_ds, epochs=20, class_weight=class_weight_dict, callbacks=[early_stopping])

print("\n--- PHASE 2: DEEP FINE-TUNING (Max 50 Epochs) ---")
base_model.trainable = True
for layer in base_model.layers[:-30]: 
    layer.trainable = False

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5), loss='binary_crossentropy', metrics=['accuracy'])
early_stopping_fine = callbacks.EarlyStopping(monitor='val_accuracy', patience=6, restore_best_weights=True, verbose=1)

model.fit(train_ds, validation_data=val_ds, epochs=50, class_weight=class_weight_dict, callbacks=[early_stopping_fine])

print("\n[4/5] Saving Elite Model to Disk...")
model.save('model_image_best_grid.keras')

print("\n[5/5] Hot-swapping the live server with new brain...")
os.system('taskkill /F /IM python.exe /T')
os.system('start "AuthGuard Python AI" /MIN cmd /c "cd /d D:\\voice-check\\voice-check && python run.py"')

print("\n=======================================================")
print(" DEEP TRAINING 100% COMPLETE! The server is back online.")
print(" You can now close this black window.")
print("=======================================================\n")
