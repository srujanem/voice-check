import os
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras import layers, models, regularizers
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

BASE_DIR = 'dataset_image'
img_size = (150, 150)
batch_size = 32

print("Loading dataset...")
full_dataset = tf.keras.utils.image_dataset_from_directory(
    BASE_DIR,
    image_size=img_size,
    batch_size=batch_size,
    shuffle=True,
    seed=42
)

# Extract labels for class weights
labels = []
for images, class_labels in full_dataset.unbatch():
    labels.append(class_labels.numpy())
labels = np.array(labels)

class_weights_arr = compute_class_weight(class_weight='balanced', classes=np.unique(labels), y=labels)
class_weight_dict = {i: weight for i, weight in enumerate(class_weights_arr)}
print("Class weights:", class_weight_dict)

total_batches = len(full_dataset)
train_size = int(0.8 * total_batches)
train_ds = full_dataset.take(train_size)
val_ds = full_dataset.skip(train_size)

# Data augmentation
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1)
])

train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y), num_parallel_calls=tf.data.AUTOTUNE)
train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

print("Building Model...")
base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(150, 150, 3))
base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.5),
    layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print("Training Classifier Head...")
model.fit(train_ds, validation_data=val_ds, epochs=3, class_weight=class_weight_dict)

print("Unfreezing top 20 layers for Fine-Tuning...")
base_model.trainable = True
for layer in base_model.layers[:-20]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print("Fine-tuning model...")
history = model.fit(train_ds, validation_data=val_ds, epochs=3, class_weight=class_weight_dict)

val_loss, val_acc = model.evaluate(val_ds)
print(f"\n--- FINAL VALIDATION ACCURACY ---")
print(f"Accuracy: {val_acc*100:.2f}%")

model.save('model_image_best_grid.keras')
print("Model saved to model_image_best_grid.keras")

with open('accuracy_report.txt', 'w') as f:
    f.write(str(val_acc * 100))
