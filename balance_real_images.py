"""
Balance real images to match fake count (650 each)
Augments existing real images with random flips, rotations, brightness, crops
"""
import os, random, sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageEnhance

REAL_DIR = "dataset_image_balanced/real"
TARGET   = 650

real_files = [f for f in os.listdir(REAL_DIR) if f.lower().endswith(('.jpg','.jpeg','.png','.webp','.bmp'))]
current    = len(real_files)
needed     = TARGET - current

print(f"Current real images : {current}")
print(f"Target              : {TARGET}")
print(f"Need to add         : {needed}")
print()

if needed <= 0:
    print("Already balanced! Nothing to do.")
    exit(0)

def augment(img):
    ops = []
    if random.random() > 0.4:
        ops.append(lambda x: x.transpose(Image.FLIP_LEFT_RIGHT))
    if random.random() > 0.4:
        angle = random.uniform(-25, 25)
        ops.append(lambda x, a=angle: x.rotate(a, expand=False, fillcolor=(0,0,0)))
    if random.random() > 0.4:
        f = random.uniform(0.75, 1.3)
        ops.append(lambda x, f=f: ImageEnhance.Brightness(x).enhance(f))
    if random.random() > 0.4:
        f = random.uniform(0.75, 1.3)
        ops.append(lambda x, f=f: ImageEnhance.Contrast(x).enhance(f))
    if random.random() > 0.5:
        w, h = img.size
        p = random.uniform(0.78, 0.95)
        nw, nh = int(w*p), int(h*p)
        l, t = random.randint(0, w-nw), random.randint(0, h-nh)
        ops.append(lambda x, l=l,t=t,r=l+nw,b=t+nh,W=w,H=h: x.crop((l,t,r,b)).resize((W,H), Image.LANCZOS))
    result = img.copy()
    random.shuffle(ops)
    for op in ops:
        try: result = op(result)
        except: pass
    return result

added = 0
attempts = 0
source = real_files.copy()
random.shuffle(source)

print("Adding augmented real images...")
while added < needed and attempts < needed * 10:
    fname = source[attempts % len(source)]
    attempts += 1
    try:
        img = Image.open(os.path.join(REAL_DIR, fname)).convert('RGB')
        aug = augment(img)
        out_path = os.path.join(REAL_DIR, f"bal_real_{added:05d}.jpg")
        if not os.path.exists(out_path):
            aug.save(out_path, "JPEG", quality=90)
            added += 1
            if added % 50 == 0:
                print(f"  Added {added}/{needed}...")
    except:
        continue

final = len([f for f in os.listdir(REAL_DIR) if f.lower().endswith(('.jpg','.jpeg','.png'))])
print(f"\nDone! Real images: {current} → {final}")
print("Now run: python train_image_fixed.py")
