import numpy as np
from PIL import Image

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
    print(f"HF Ratio: {hf_ratio:.4f}")

test_fft('C:/Users/sruja/.gemini/antigravity/brain/14c6cba6-290a-4015-9068-c422a5c944fe/.user_uploaded/media_1787398581135.png')
