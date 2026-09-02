import numpy as np
from PIL import Image
import os, glob

def test_fft(path):
    img = Image.open(path).convert('L')
    f = np.fft.fft2(np.array(img))
    fshift = np.fft.fftshift(f)
    mag = 20 * np.log(np.abs(fshift) + 1)
    h, w = mag.shape
    y, x = np.ogrid[0:h, 0:w]
    cy, cx = h//2, w//2
    mask = (x-cx)**2 + (y-cy)**2 <= (min(h, w)*0.15)**2
    hf_ratio = np.sum(mag[~mask]) / (np.sum(mag) + 1e-10)
    return hf_ratio

files = glob.glob('D:/voice-check/voice-check/dataset_image/real/*.jpg')[:5]
for f in files:
    r = test_fft(f)
    print(f"Real -> HF Ratio: {r:.4f}")
    
files2 = glob.glob('D:/voice-check/voice-check/dataset_image/fake/*.jpg')[:5]
for f in files2:
    r = test_fft(f)
    print(f"Fake -> HF Ratio: {r:.4f}")
