import os, glob, random, cv2
import numpy as np
from PIL import Image, ImageEnhance

real_dir = 'D:/voice-check/voice-check/dataset_image/real'
fake_dir = 'D:/voice-check/voice-check/dataset_image/fake'

real_files = [f for f in glob.glob(os.path.join(real_dir, '*')) if os.path.isfile(f)]
fake_files = [f for f in glob.glob(os.path.join(fake_dir, '*')) if os.path.isfile(f)]

target = len(real_files)
current_fake = len(fake_files)
needed = target - current_fake

print(f"Target count: {target}")
print(f"Current Fake count: {current_fake}")
print(f"Generating {needed} distinct AI images...")

def generate_variant(img):
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    h, w, _ = img_cv.shape
    
    if random.random() > 0.5:
        img_cv = cv2.flip(img_cv, 1)
        
    angle = random.uniform(-12, 12)
    scale = random.uniform(0.92, 1.08)
    M = cv2.getRotationMatrix2D((w/2, h/2), angle, scale)
    img_cv = cv2.warpAffine(img_cv, M, (w, h), borderMode=cv2.BORDER_REFLECT)
    
    mode = random.choice(['noise', 'smooth', 'contrast', 'chroma', 'blur', 'sharp'])
    if mode == 'noise':
        noise = np.random.normal(0, random.uniform(2, 6), (h, w, 3)).astype(np.float32)
        img_cv = np.clip(img_cv.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    elif mode == 'smooth':
        img_cv = cv2.bilateralFilter(img_cv, 7, 50, 50)
    elif mode == 'contrast':
        alpha = random.uniform(1.05, 1.25)
        img_cv = np.clip(img_cv.astype(np.float32) * alpha, 0, 255).astype(np.uint8)
    elif mode == 'chroma':
        ycbcr = cv2.cvtColor(img_cv, cv2.COLOR_BGR2YCrCb)
        ycbcr[:,:,1] = np.clip(ycbcr[:,:,1] * random.uniform(1.1, 1.25), 0, 255).astype(np.uint8)
        img_cv = cv2.cvtColor(ycbcr, cv2.COLOR_YCrCb2BGR)
    elif mode == 'blur':
        img_cv = cv2.GaussianBlur(img_cv, (3, 3), 0)
    else:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        img_cv = cv2.filter2D(img_cv, -1, kernel)
        
    out_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
    enh = ImageEnhance.Color(out_pil).enhance(random.uniform(0.9, 1.3))
    return enh

created = 0
for i in range(needed):
    src = fake_files[i % len(fake_files)]
    try:
        with Image.open(src) as im:
            v = generate_variant(im.convert('RGB'))
            out_path = os.path.join(fake_dir, f"ai_matched_synth_{i+1}.jpg")
            v.save(out_path, format='JPEG', quality=random.randint(86, 96))
            created += 1
            if created % 500 == 0 or created == needed:
                print(f"Created {created}/{needed} matched AI images ({int(created/needed*100)}%)...")
    except Exception as e:
        pass

final_real = len([f for f in glob.glob(os.path.join(real_dir, '*')) if os.path.isfile(f)])
final_fake = len([f for f in glob.glob(os.path.join(fake_dir, '*')) if os.path.isfile(f)])
print(f"MATCH COMPLETE: Real: {final_real} | Fake: {final_fake} | Exactly Matched: {final_real == final_fake}")
