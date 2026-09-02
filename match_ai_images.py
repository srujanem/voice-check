import os, glob, random, cv2, hashlib
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

real_dir = 'D:/voice-check/voice-check/dataset_image/real'
fake_dir = 'D:/voice-check/voice-check/dataset_image/fake'

real_files = [f for f in glob.glob(os.path.join(real_dir, '*')) if os.path.isfile(f)]
fake_files = [f for f in glob.glob(os.path.join(fake_dir, '*')) if os.path.isfile(f)]

target = len(real_files)
current_fake = len(fake_files)
needed = target - current_fake

print(f"Target count: {target}")
print(f"Current Fake count: {current_fake}")
print(f"Generating {needed} distinct AI images to match exactly...")

def get_dhash(img, hash_size=8):
    gray = img.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.BOX)
    arr = np.array(gray)
    diff = arr[:, 1:] > arr[:, :-1]
    return tuple(diff.flatten().tolist())

# Index existing hashes
existing_hashes = set()
for f in fake_files:
    try:
        with Image.open(f) as im:
            existing_hashes.add(get_dhash(im))
    except: pass

def generate_distinct_ai_variant(img, idx):
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    h, w, _ = img_cv.shape
    
    # 1. Random geometric transform
    if random.random() > 0.5:
        img_cv = cv2.flip(img_cv, 1)
    
    angle = random.uniform(-15, 15)
    M = cv2.getRotationMatrix2D((w/2, h/2), angle, random.uniform(0.9, 1.1))
    img_cv = cv2.warpAffine(img_cv, M, (w, h), borderMode=cv2.BORDER_REFLECT)
    
    # 2. Diffusion / Generative style filter
    mode = random.choice([
        'latent_diffusion_noise',
        'neural_color_grade',
        'bilateral_airbrush',
        'unsharp_pop',
        'chrominance_boost',
        'spectral_blur'
    ])
    
    if mode == 'latent_diffusion_noise':
        noise = np.random.normal(0, random.uniform(3, 8), (h, w, 3)).astype(np.float32)
        img_cv = np.clip(img_cv.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    elif mode == 'neural_color_grade':
        yuv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2YUV)
        yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
        img_cv = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
    elif mode == 'bilateral_airbrush':
        img_cv = cv2.bilateralFilter(img_cv, 9, 75, 75)
    elif mode == 'chrominance_boost':
        ycbcr = cv2.cvtColor(img_cv, cv2.COLOR_BGR2YCrCb)
        ycbcr[:,:,1] = np.clip(ycbcr[:,:,1] * random.uniform(1.1, 1.3), 0, 255).astype(np.uint8)
        img_cv = cv2.cvtColor(ycbcr, cv2.COLOR_YCrCb2BGR)
    elif mode == 'unsharp_pop':
        gaussian = cv2.GaussianBlur(img_cv, (0, 0), 2.0)
        img_cv = cv2.addWeighted(img_cv, 1.5, gaussian, -0.5, 0)
    else: # spectral_blur
        img_cv = cv2.medianBlur(img_cv, 3)
        
    out_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
    
    # Slight color/contrast variance
    enh = ImageEnhance.Color(out_pil).enhance(random.uniform(0.85, 1.35))
    enh = ImageEnhance.Contrast(enh).enhance(random.uniform(0.9, 1.25))
    return enh

created = 0
attempts = 0
max_attempts = needed * 4

while created < needed and attempts < max_attempts:
    attempts += 1
    src = random.choice(fake_files)
    try:
        with Image.open(src) as base_im:
            variant = generate_distinct_ai_variant(base_im.convert('RGB'), created)
            dh = get_dhash(variant)
            if dh not in existing_hashes:
                existing_hashes.add(dh)
                out_path = os.path.join(fake_dir, f"ai_matched_gen_{created+1}.jpg")
                variant.save(out_path, format='JPEG', quality=random.randint(86, 96))
                created += 1
                if created % 500 == 0 or created == needed:
                    print(f"Created {created}/{needed} matched AI images ({int(created/needed*100)}%)...")
    except: pass

final_real = len(glob.glob(os.path.join(real_dir, '*')))
final_fake = len(glob.glob(os.path.join(fake_dir, '*')))
print(f"Final Count -> Real: {final_real} | Fake: {final_fake} | Balanced: {final_real == final_fake}")
