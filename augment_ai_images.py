"""
Generate synthetic AI-style training images by augmenting the existing 13 real AI (Gemini) images
using heavy augmentation - flips, rotations, color shifts, blurs, noise.
This gives us ~300 AI training images from 13 real ones, enough for a balanced dataset.
"""
import os, shutil, random
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

FAKE_DIR = "dataset_image/fake"
BALANCED_FAKE_DIR = "dataset_image_balanced/fake"

# Get existing real AI images (Gemini generated)
gemini_images = [f for f in os.listdir(FAKE_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
print(f"Base AI images to augment: {len(gemini_images)}")

# Clear balanced fake dir and rebuild it with augmented images
if os.path.exists(BALANCED_FAKE_DIR):
    shutil.rmtree(BALANCED_FAKE_DIR)
os.makedirs(BALANCED_FAKE_DIR)

TARGET = 150  # We want 150 augmented fake images
generated = 0

random.seed(42)
np.random.seed(42)

def augment_image(img, idx):
    """Apply random augmentation to create new fake training samples."""
    augmentations = []
    
    # Random horizontal flip
    if random.random() > 0.5:
        img = ImageOps.mirror(img)
    
    # Random rotation (-15 to +15 degrees)
    angle = random.uniform(-15, 15)
    img = img.rotate(angle, fillcolor=(128, 128, 128))
    
    # Random brightness
    factor = random.uniform(0.7, 1.3)
    img = ImageEnhance.Brightness(img).enhance(factor)
    
    # Random contrast
    factor = random.uniform(0.8, 1.2)
    img = ImageEnhance.Contrast(img).enhance(factor)
    
    # Random color saturation
    factor = random.uniform(0.8, 1.2)
    img = ImageEnhance.Color(img).enhance(factor)
    
    # Random blur (sometimes)
    if random.random() > 0.6:
        radius = random.uniform(0.5, 1.5)
        img = img.filter(ImageFilter.GaussianBlur(radius=radius))
    
    # Random sharpening (sometimes)
    if random.random() > 0.6:
        factor = random.uniform(1.2, 2.0)
        img = ImageEnhance.Sharpness(img).enhance(factor)
    
    # Add slight noise
    img_array = np.array(img).astype(np.float32)
    noise = np.random.normal(0, 5, img_array.shape)
    img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_array)
    
    # Random crop and resize back
    w, h = img.size
    crop_pct = random.uniform(0.85, 1.0)
    new_w, new_h = int(w * crop_pct), int(h * crop_pct)
    left = random.randint(0, w - new_w)
    top = random.randint(0, h - new_h)
    img = img.crop((left, top, left + new_w, top + new_h))
    img = img.resize((224, 224), Image.LANCZOS)
    
    return img

# Generate augmented images
per_image = (TARGET // len(gemini_images)) + 2
print(f"Generating ~{per_image} variants per base AI image...")

for base_name in gemini_images:
    src = os.path.join(FAKE_DIR, base_name)
    base_img = Image.open(src).convert('RGB').resize((224, 224))
    
    # Always include the original
    out_path = os.path.join(BALANCED_FAKE_DIR, f"ai_orig_{base_name}")
    base_img.save(out_path)
    generated += 1
    
    # Generate augmented versions
    for i in range(per_image):
        if generated >= TARGET:
            break
        aug = augment_image(base_img.copy(), i)
        name_stem = os.path.splitext(base_name)[0]
        out_path = os.path.join(BALANCED_FAKE_DIR, f"ai_aug_{name_stem}_{i:03d}.jpg")
        aug.save(out_path, "JPEG", quality=90)
        generated += 1
    
    if generated >= TARGET:
        break

print(f"Generated {generated} AI training images in {BALANCED_FAKE_DIR}")

# Now balance the real images too
BALANCED_REAL_DIR = "dataset_image_balanced/real"
if os.path.exists(BALANCED_REAL_DIR):
    shutil.rmtree(BALANCED_REAL_DIR)
os.makedirs(BALANCED_REAL_DIR)

real_files = os.listdir("dataset_image/real")
random.shuffle(real_files)
count = 0
for f in real_files[:generated]:  # Match same count as fake
    shutil.copy2(os.path.join("dataset_image/real", f),
                 os.path.join(BALANCED_REAL_DIR, f))
    count += 1

print(f"Copied {count} real images to {BALANCED_REAL_DIR}")
print(f"\nFinal balanced dataset: {generated} fake + {count} real = {generated+count} total")
print("Now run: python train_image.py")
