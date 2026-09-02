# -*- coding: utf-8 -*-
import os, glob, random, cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

print("==========================================================")
print("     AUTHGUARD AI - SYNTHETIC AI IMAGE GENERATOR          ")
print("==========================================================")

real_dir = 'D:/voice-check/voice-check/dataset_image/real'
fake_dir = 'D:/voice-check/voice-check/dataset_image/fake'

real_files = [f for f in glob.glob(os.path.join(real_dir, '*')) if os.path.isfile(f)]
fake_files = [f for f in glob.glob(os.path.join(fake_dir, '*')) if os.path.isfile(f)]

target_count = len(real_files)
needed = target_count - len(fake_files)

print(f"Target count per class: {target_count}")
print(f"Current Fake count: {len(fake_files)}")
print(f"Generating {needed} new synthetic AI images to equalize...")

def apply_synthetic_diffusion_transform(img):
    """Applies diverse diffusion / generative artifact transformations."""
    mode = random.choice(['latent_smooth', 'chroma_shift', 'spectral_noise', 'style_mix', 'grid_resample', 'contrast_pop'])
    
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    h, w, _ = img_cv.shape
    
    if mode == 'latent_smooth':
        # Bilateral filter for smooth AI face texture
        d = random.choice([5, 9, 13])
        sigma = random.uniform(50, 100)
        smoothed = cv2.bilateralFilter(img_cv, d, sigma, sigma)
        out = Image.fromarray(cv2.cvtColor(smoothed, cv2.COLOR_BGR2RGB))
        
    elif mode == 'chroma_shift':
        # AI chrominance exaggeration
        ycbcr = cv2.cvtColor(img_cv, cv2.COLOR_BGR2YCrCb)
        ycbcr[:, :, 1] = cv2.multiply(ycbcr[:, :, 1], random.uniform(1.05, 1.25))
        ycbcr[:, :, 2] = cv2.multiply(ycbcr[:, :, 2], random.uniform(0.95, 1.20))
        shifted = cv2.cvtColor(ycbcr, cv2.COLOR_YCrCb2RGB)
        out = Image.fromarray(shifted)
        
    elif mode == 'spectral_noise':
        # Subtle high-frequency diffusion latent noise
        noise = np.random.normal(0, random.uniform(2, 6), (h, w, 3)).astype(np.float32)
        noisy = np.clip(img_cv.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        out = Image.fromarray(cv2.cvtColor(noisy, cv2.COLOR_BGR2RGB))
        
    elif mode == 'style_mix':
        # Color temperature & saturation boost
        pil_img = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
        enh_col = ImageEnhance.Color(pil_img).enhance(random.uniform(1.1, 1.35))
        enh_con = ImageEnhance.Contrast(enh_col).enhance(random.uniform(1.05, 1.25))
        out = enh_con
        
    elif mode == 'grid_resample':
        # Subtle upsample/downsample interpolation artifact
        scale = random.uniform(0.75, 1.25)
        new_w, new_h = max(100, int(w * scale)), max(100, int(h * scale))
        resized = cv2.resize(img_cv, (new_w, new_h), interpolation=random.choice([cv2.INTER_CUBIC, cv2.INTER_LANCZOS4]))
        restored = cv2.resize(resized, (w, h), interpolation=cv2.INTER_LINEAR)
        out = Image.fromarray(cv2.cvtColor(restored, cv2.COLOR_BGR2RGB))
        
    else: # contrast_pop
        pil_img = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
        out = ImageEnhance.Sharpness(pil_img).enhance(random.uniform(1.2, 1.6))
        
    # Apply random flip / rotation
    if random.random() > 0.5:
        out = out.transpose(Image.FLIP_LEFT_RIGHT)
    if random.random() > 0.7:
        out = out.rotate(random.uniform(-8, 8), resample=Image.BICUBIC)
        
    return out

generated_count = 0
while generated_count < needed:
    src_file = random.choice(fake_files)
    try:
        with Image.open(src_file) as im:
            rgb_im = im.convert('RGB')
            synth_im = apply_synthetic_diffusion_transform(rgb_im)
            out_name = f"synth_ai_gen_{generated_count + 1}.jpg"
            out_path = os.path.join(fake_dir, out_name)
            synth_im.save(out_path, format='JPEG', quality=random.randint(85, 95))
            generated_count += 1
            if generated_count % 500 == 0 or generated_count == needed:
                print(f"Generated {generated_count}/{needed} synthetic AI images ({int(generated_count/needed*100)}%)...")
    except Exception as e:
        continue

final_real = len(glob.glob(os.path.join(real_dir, '*')))
final_fake = len(glob.glob(os.path.join(fake_dir, '*')))

print("\n==========================================================")
print(f"SUCCESS! Dataset Equalized:")
print(f"  - Real Images: {final_real}")
print(f"  - Fake (AI) Images: {final_fake}")
print(f"  - Total Balanced Images: {final_real + final_fake}")
print("==========================================================")
