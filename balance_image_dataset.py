import os
import random
import uuid
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

FAKE_DIR = r"D:\voice-check\voice-check\dataset_image\fake"
REAL_DIR = r"D:\voice-check\voice-check\dataset_image\real"

fake_images = [f for f in os.listdir(FAKE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
real_count = len([f for f in os.listdir(REAL_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
fake_count = len(fake_images)

print(f"Current balance: {real_count} Real vs {fake_count} Fake")

deficit = real_count - fake_count

if deficit > 0:
    print(f"Generating {deficit} augmented AI images to balance the dataset...")
    
    for i in range(deficit):
        # Pick a random base fake image
        base_img_name = random.choice(fake_images)
        base_img_path = os.path.join(FAKE_DIR, base_img_name)
        
        try:
            img = Image.open(base_img_path).convert('RGB')
            
            # 1. Random Flip
            if random.random() > 0.5:
                img = ImageOps.mirror(img)
                
            # 2. Random Color Jitter (Brightness/Contrast)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(random.uniform(0.7, 1.3))
            
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(random.uniform(0.8, 1.2))
            
            # 3. Random Slight Rotation (-10 to 10 degrees)
            if random.random() > 0.5:
                img = img.rotate(random.uniform(-10, 10))
                
            # 4. Save with random JPEG compression artifacts to simulate web
            save_path = os.path.join(FAKE_DIR, f"aug_{uuid.uuid4().hex[:8]}.jpg")
            img.save(save_path, "JPEG", quality=random.randint(40, 95))
            
        except Exception as e:
            print(f"Error augmenting {base_img_name}: {e}")
            
    print("Dataset balanced perfectly!")
else:
    print("Dataset is already balanced or has excess fake images.")
