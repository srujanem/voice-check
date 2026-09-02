import os, io, cv2
import numpy as np
from PIL import Image, ImageChops

def analyze_image_forensics(img_path):
    img = Image.open(img_path).convert('RGB')
    w, h = img.size
    
    gray_u8 = np.array(img.convert('L'), dtype=np.uint8)
    gray = np.array(img.convert('L'), dtype=np.float32)
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    mag = 20 * np.log(np.abs(fshift) + 1e-6)
    
    cy, cx = h // 2, w // 2
    y, x = np.ogrid[0:h, 0:w]
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    
    low_mask = r < (min(h, w) * 0.1)
    high_mask = r > (min(h, w) * 0.35)
    
    high_energy = float(np.mean(mag[high_mask]))
    low_energy = float(np.mean(mag[low_mask]))
    spectral_decay = low_energy / (high_energy + 1e-6)
    
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=90)
    buf.seek(0)
    resaved = Image.open(buf)
    ela = ImageChops.difference(img, resaved)
    ela_arr = np.array(ela, dtype=np.float32)
    ela_mean = float(np.mean(ela_arr))
    ela_std = float(np.std(ela_arr))
    
    ycbcr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2YCrCb)
    cb_std = float(np.std(ycbcr[:, :, 1]))
    cr_std = float(np.std(ycbcr[:, :, 2]))
    chroma_var = (cb_std + cr_std) / 2.0
    
    laplacian = cv2.Laplacian(gray_u8, cv2.CV_64F)
    lap_var = float(laplacian.var())
    
    print(f'File: {os.path.basename(img_path)}')
    print(f'  Spectral Decay: {spectral_decay:.2f} | High Energy: {high_energy:.2f}')
    print(f'  ELA Mean: {ela_mean:.2f} | ELA Std: {ela_std:.2f}')
    print(f'  Chroma Var: {chroma_var:.2f} | Laplacian: {lap_var:.2f}')

artifacts = [
    ('REAL Camera Photo 1', 'C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787474543971.png'),
    ('REAL Camera Photo 2', 'C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787398581135.png'),
    ('AI Generated Face 1', 'C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787396274505.jpg'),
    ('AI Generated Face 2', 'C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/realistic_indian_man_1787399535686.jpg'),
    ('AI Graphic/Art 1', 'C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787399134182.png')
]

for label, p in artifacts:
    if os.path.exists(p):
        print(f'=== {label} ===')
        analyze_image_forensics(p)
