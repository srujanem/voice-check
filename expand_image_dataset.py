"""
Expand image dataset using multiple public sources:
  1. HuggingFace: cifake (correct dataset name), imagenet_sketch, etc.
  2. Fallback: Download AI images from public URLs

Goal: Add 500 fake + 500 real images to dataset_image_balanced/
Then retrain for better generalization.
"""

import os, sys, io, random, time
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

FAKE_DIR = "dataset_image_balanced/fake"
REAL_DIR = "dataset_image_balanced/real"
os.makedirs(FAKE_DIR, exist_ok=True)
os.makedirs(REAL_DIR, exist_ok=True)

TARGET_NEW = 500

current_fake = len([f for f in os.listdir(FAKE_DIR) if f.lower().endswith(('.jpg','.jpeg','.png'))])
current_real = len([f for f in os.listdir(REAL_DIR) if f.lower().endswith(('.jpg','.jpeg','.png'))])
print(f"Current: {current_real} real | {current_fake} fake")
print(f"Target:  {current_real + TARGET_NEW} real | {current_fake + TARGET_NEW} fake")
print()

fake_added = 0
real_added = 0

def save_pil(img, folder, prefix, idx):
    try:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        if min(img.size) < 32:
            return False
        # Upscale small images to at least 128x128
        if min(img.size) < 128:
            new_size = (max(img.width, 128), max(img.height, 128))
            img = img.resize(new_size, Image.LANCZOS)
        path = os.path.join(folder, f"{prefix}_{idx:05d}.jpg")
        if os.path.exists(path):
            return False
        img.save(path, "JPEG", quality=90)
        return True
    except:
        return False

# ── Method 1: HuggingFace CIFAKE (correct dataset ID) ─────────────────────
print("=" * 55)
print("Trying: HuggingFace CIFAKE dataset (Parquet format)...")
print("=" * 55)

try:
    from datasets import load_dataset

    # Try the correct dataset - 'cifake' by ghostbuster or similar
    dataset_options = [
        ("Saka/CIFAKE_resampled", "train", "image", "label", 0, 1),
        ("SahandNZ/cifake", "train", "image", "label", 0, 1),
    ]

    success = False
    for ds_name, split, img_col, lbl_col, real_lbl, fake_lbl in dataset_options:
        if fake_added >= TARGET_NEW and real_added >= TARGET_NEW:
            break
        try:
            print(f"  Trying: {ds_name}...")
            ds = load_dataset(ds_name, split=split, streaming=True)
            processed = 0
            for item in ds:
                if fake_added >= TARGET_NEW and real_added >= TARGET_NEW:
                    break
                processed += 1
                if processed % 100 == 0:
                    print(f"    Processed {processed} | Fake:{fake_added}/{TARGET_NEW} Real:{real_added}/{TARGET_NEW}")
                try:
                    img = item[img_col]
                    label = item[lbl_col]
                    if label == fake_lbl and fake_added < TARGET_NEW:
                        if save_pil(img, FAKE_DIR, f"hf_fake", current_fake + fake_added):
                            fake_added += 1
                    elif label == real_lbl and real_added < TARGET_NEW:
                        if save_pil(img, REAL_DIR, f"hf_real", current_real + real_added):
                            real_added += 1
                except:
                    continue
            if fake_added > 0 or real_added > 0:
                print(f"  Success with {ds_name}: +{fake_added} fake, +{real_added} real")
                success = True
                break
        except Exception as e:
            print(f"  Failed: {e}")
            continue

except Exception as e:
    print(f"HuggingFace error: {e}")

# ── Method 2: Augment existing images ─────────────────────────────────────
print()
print("=" * 55)
print("Augmenting existing images (flip/rotate/crop/brightness)...")
print("=" * 55)

import numpy as np

def augment_image(img):
    """Apply random augmentation to create a new variant."""
    ops = []
    if random.random() > 0.5:
        ops.append(lambda x: x.transpose(Image.FLIP_LEFT_RIGHT))
    if random.random() > 0.5:
        angle = random.uniform(-30, 30)
        ops.append(lambda x, a=angle: x.rotate(a, expand=False))
    if random.random() > 0.5:
        from PIL import ImageEnhance
        factor = random.uniform(0.7, 1.3)
        ops.append(lambda x, f=factor: ImageEnhance.Brightness(x).enhance(f))
    if random.random() > 0.5:
        from PIL import ImageEnhance
        factor = random.uniform(0.7, 1.3)
        ops.append(lambda x, f=factor: ImageEnhance.Contrast(x).enhance(f))
    # Crop + resize
    if random.random() > 0.5:
        w, h = img.size
        crop_pct = random.uniform(0.75, 0.95)
        new_w, new_h = int(w * crop_pct), int(h * crop_pct)
        left = random.randint(0, w - new_w)
        top  = random.randint(0, h - new_h)
        ops.append(lambda x, l=left, t=top, r=left+new_w, b=top+new_h: x.crop((l, t, r, b)).resize((w, h), Image.LANCZOS))

    result = img.copy()
    for op in ops:
        try:
            result = op(result)
        except:
            pass
    return result

# Augment fake images
fake_files = [f for f in os.listdir(FAKE_DIR) if f.lower().endswith(('.jpg','.jpeg','.png'))][:150]
aug_fake = 0
random.shuffle(fake_files)
for fname in fake_files * 5:  # cycle through multiple times
    if fake_added >= TARGET_NEW:
        break
    try:
        img = Image.open(os.path.join(FAKE_DIR, fname)).convert('RGB')
        aug = augment_image(img)
        if save_pil(aug, FAKE_DIR, "aug_fake", current_fake + fake_added):
            fake_added += 1
            aug_fake += 1
    except:
        continue

print(f"  Fake augmentations added: {aug_fake}")

# Augment real images
real_files = [f for f in os.listdir(REAL_DIR) if f.lower().endswith(('.jpg','.jpeg','.png'))][:150]
aug_real = 0
random.shuffle(real_files)
for fname in real_files * 5:
    if real_added >= TARGET_NEW:
        break
    try:
        img = Image.open(os.path.join(REAL_DIR, fname)).convert('RGB')
        aug = augment_image(img)
        if save_pil(aug, REAL_DIR, "aug_real", current_real + real_added):
            real_added += 1
            aug_real += 1
    except:
        continue

print(f"  Real augmentations added: {aug_real}")

# ── Method 3: Download real photos from picsum ───────────────────────────
if real_added < TARGET_NEW:
    import requests
    print()
    print("Downloading real photos from picsum.photos...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    seed = current_real + 9000
    for i in range(TARGET_NEW - real_added):
        try:
            url = f"https://picsum.photos/seed/{seed + i}/256/256"
            r = requests.get(url, timeout=12, headers=headers)
            img = Image.open(io.BytesIO(r.content))
            if save_pil(img, REAL_DIR, "web_real", current_real + real_added):
                real_added += 1
                if real_added % 50 == 0:
                    print(f"  Real from web: {real_added}/{TARGET_NEW}")
        except Exception as e:
            time.sleep(0.2)
            continue
    print(f"  Real web downloads: {real_added}")

# ── Final report ─────────────────────────────────────────────────────────
final_fake = len([f for f in os.listdir(FAKE_DIR) if f.lower().endswith(('.jpg','.jpeg','.png'))])
final_real = len([f for f in os.listdir(REAL_DIR) if f.lower().endswith(('.jpg','.jpeg','.png'))])

print()
print("=" * 55)
print(f"DONE! Final dataset:")
print(f"  Real: {final_real} images (+{final_real - current_real} new)")
print(f"  Fake: {final_fake} images (+{final_fake - current_fake} new)")
print("=" * 55)
print()
print("Now run: python train_image_fixed.py")
print("to retrain on the expanded dataset.")
