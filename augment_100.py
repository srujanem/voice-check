import os
import random
from PIL import Image, ImageEnhance, ImageFilter
import uuid

FAKE_DIR = r"D:\voice-check\voice-check\dataset_image\fake"
os.makedirs(FAKE_DIR, exist_ok=True)

existing = [f for f in os.listdir(FAKE_DIR) if f.endswith('.jpg') or f.endswith('.png')]
if not existing:
    print("No images to augment.")
    exit()

count = 0
for i in range(100):
    try:
        src = os.path.join(FAKE_DIR, random.choice(existing))
        with Image.open(src) as img:
            img = img.convert('RGB')
            # Random augmentations
            if random.random() > 0.5:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            if random.random() > 0.5:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(random.uniform(0.7, 1.3))
            if random.random() > 0.5:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(random.uniform(0.8, 1.2))
            if random.random() > 0.8:
                img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))
                
            new_name = f"aug_ai_{uuid.uuid4().hex[:8]}.jpg"
            img.save(os.path.join(FAKE_DIR, new_name))
            count += 1
    except Exception as e:
        print(e)

print(f"Successfully generated {count} augmented AI images!")
os.system("python train_image_advanced.py")
