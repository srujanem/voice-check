import os
import glob
import shutil

source_dir = r'D:\images'
dest_dir = r'D:\voice-check\voice-check\dataset_custom\real'

os.makedirs(dest_dir, exist_ok=True)

images = glob.glob(os.path.join(source_dir, '*.*'))
count = 0

for img_path in images:
    if img_path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        filename = os.path.basename(img_path)
        # Clean up filename
        safe_name = filename.replace(' ', '_').replace('(', '').replace(')', '').replace('.jpeg', '.jpg')
        new_path = os.path.join(dest_dir, f"whatsapp_{safe_name}")
        shutil.copy2(img_path, new_path)
        count += 1

print(f"Successfully transferred {count} images to the 'Real' dataset folder!")
