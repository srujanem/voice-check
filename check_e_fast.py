# -*- coding: utf-8 -*-
import glob, os, hashlib

real_dir = 'D:/voice-check/voice-check/dataset_image/real'
existing_sizes = {}
for f in glob.glob(os.path.join(real_dir, '*')):
    if os.path.isfile(f):
        try:
            sz = os.path.getsize(f)
            if sz not in existing_sizes:
                existing_sizes[sz] = []
            with open(f, 'rb') as fp:
                existing_sizes[sz].append(hashlib.md5(fp.read(32768)).hexdigest())
        except: pass

print(f"Indexed existing dataset images: {len(glob.glob(os.path.join(real_dir, '*')))}")

folders = [
    ('E:/family pics real', 'Family Pics Real'),
    ('E:/srujan phone pics', 'Srujan Phone Pics')
]

total_found = 0
total_new = 0
image_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.heic'}

for path, label in folders:
    all_imgs = []
    for root, _, files in os.walk(path):
        for f in files:
            if os.path.splitext(f)[1].lower() in image_exts:
                all_imgs.append(os.path.join(root, f))
    
    new_imgs = 0
    duplicate_imgs = 0
    for img in all_imgs:
        try:
            sz = os.path.getsize(img)
            if sz in existing_sizes:
                with open(img, 'rb') as fp:
                    h = hashlib.md5(fp.read(32768)).hexdigest()
                if h in existing_sizes[sz]:
                    duplicate_imgs += 1
                    continue
            new_imgs += 1
        except: pass
        
    print(f"\nFolder: {label} ({path})")
    print(f"   - Total images: {len(all_imgs)}")
    print(f"   - Already in dataset: {duplicate_imgs}")
    print(f"   - Brand new (NOT in dataset): {new_imgs}")
    total_found += len(all_imgs)
    total_new += new_imgs

print("\n" + "="*50)
print(f"SUMMARY FOR E: DRIVE:")
print(f"   - Total Images Found: {total_found}")
print(f"   - New Images NOT in Dataset: {total_new}")
print("="*50)
