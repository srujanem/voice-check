import os, glob, hashlib
import numpy as np
from PIL import Image

fake_dir = 'D:/voice-check/voice-check/dataset_image/fake'
files = glob.glob(os.path.join(fake_dir, '*'))
print(f"Total files in AI dataset: {len(files)}")

def fast_dhash(img_path):
    try:
        with Image.open(img_path) as img:
            gray = img.convert('L').resize((9, 8), Image.Resampling.BOX)
            arr = np.array(gray)
            diff = arr[:, 1:] > arr[:, :-1]
            return tuple(diff.flatten().tolist())
    except:
        return None

seen_md5 = set()
seen_dhash = set()
deleted_exact = 0
deleted_perceptual = 0

for i, f in enumerate(files):
    if not os.path.isfile(f): continue
    
    # Exact hash
    sz = os.path.getsize(f)
    with open(f, 'rb') as fp:
        m = hashlib.md5(f"{sz}".encode() + fp.read()).hexdigest()
    
    if m in seen_md5:
        try:
            os.remove(f)
            deleted_exact += 1
            continue
        except: pass
    seen_md5.add(m)
    
    # Perceptual hash
    dh = fast_dhash(f)
    if dh:
        if dh in seen_dhash:
            try:
                os.remove(f)
                deleted_perceptual += 1
                continue
            except: pass
        seen_dhash.add(dh)

remaining = len(glob.glob(os.path.join(fake_dir, '*')))
print(f"Exact binary duplicates deleted: {deleted_exact}")
print(f"Perceptual visual duplicates deleted: {deleted_perceptual}")
print(f"Total overlapping duplicates deleted: {deleted_exact + deleted_perceptual}")
print(f"Remaining clean unique AI images: {remaining}")
