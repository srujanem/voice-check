import glob, os, hashlib

real_dir = 'D:/voice-check/voice-check/dataset_image/real'
existing_hashes = set()
for f in glob.glob(os.path.join(real_dir, '*')):
    if os.path.isfile(f):
        try:
            sz = os.path.getsize(f)
            with open(f, 'rb') as fp:
                existing_hashes.add(hashlib.md5(str(sz).encode() + fp.read(32768)).hexdigest())
        except: pass

print(f"Total indexed dataset real images: {len(existing_hashes)}")

e_folders = ['E:/family pics real', 'E:/srujan phone pics']
image_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.heic', '.dng'}

total_found_all = 0
total_new_all = 0

for folder in e_folders:
    if os.path.exists(folder):
        all_imgs = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if os.path.splitext(file)[1].lower() in image_exts:
                    all_imgs.append(os.path.join(root, file))
                    
        new_count = 0
        duplicate_count = 0
        for img_path in all_imgs:
            try:
                sz = os.path.getsize(img_path)
                with open(img_path, 'rb') as fp:
                    h = hashlib.md5(str(sz).encode() + fp.read(32768)).hexdigest()
                if h in existing_hashes:
                    duplicate_count += 1
                else:
                    new_count += 1
            except: pass
            
        print(f"\nFolder: '{folder}'")
        print(f"  - Total pictures found: {len(all_imgs)}")
        print(f"  - Already in dataset: {duplicate_count}")
        print(f"  - Brand new (NOT in dataset): {new_count}")
        
        total_found_all += len(all_imgs)
        total_new_all += new_count

print(f"\n==========================================================")
print(f"TOTAL ON E: DRIVE:")
print(f"  - Total Photos Found: {total_found_all}")
print(f"  - New Photos NOT in Dataset: {total_new_all}")
print(f"==========================================================")
