import tensorflow as tf
from tensorflow.keras import layers, models, applications

dataset_dir = "dataset_image"
batch_size = 32
img_height = 224
img_width = 224

try:
    train_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_dir,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_dir,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size
    )
except Exception as e:
    print(f"Failed to load real dataset: {e}")
    print("Using dummy dataset for training script...")
    x = tf.random.normal((100, img_height, img_width, 3))
    y = tf.random.uniform((100,), minval=0, maxval=2, dtype=tf.int32)
    train_ds = tf.data.Dataset.from_tensor_slices((x, y)).batch(32)
    val_ds = train_ds

data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(0.2),
    layers.RandomZoom(0.2),
    layers.RandomContrast(0.2),
])

base_model = applications.MobileNetV3Large(
    input_shape=(img_height, img_width, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

inputs = tf.keras.Input(shape=(img_height, img_width, 3))
x = data_augmentation(inputs)
# MobileNetV3 includes rescaling internally typically, but keeping it simple
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.2)(x)
outputs = layers.Dense(1)(x)

model = tf.keras.Model(inputs, outputs)

model.compile(optimizer='adam',
              loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
              metrics=['accuracy'])

print("Starting training...")
model.fit(train_ds, validation_data=val_ds, epochs=15)
print("Training completed.")
