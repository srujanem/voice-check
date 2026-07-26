import os
import numpy as np
from PIL import Image

def generate_dummy_dataset():
    print("="*60)
    print("Generating a quick dummy image dataset for testing...")
    print("="*60)
    
    real_dir = os.path.join("dataset_image", "real")
    fake_dir = os.path.join("dataset_image", "fake")
    os.makedirs(real_dir, exist_ok=True)
    os.makedirs(fake_dir, exist_ok=True)
    
    # Generate 50 real and 50 fake images
    for i in range(50):
        # Real images: Slightly reddish random noise
        real_img_array = np.random.randint(0, 200, (224, 224, 3), dtype=np.uint8)
        real_img_array[:, :, 0] = np.random.randint(150, 255, (224, 224), dtype=np.uint8) # More red
        img = Image.fromarray(real_img_array)
        img.save(os.path.join(real_dir, f"dummy_real_{i}.jpg"))
        
        # Fake images: Slightly blueish random noise
        fake_img_array = np.random.randint(0, 200, (224, 224, 3), dtype=np.uint8)
        fake_img_array[:, :, 2] = np.random.randint(150, 255, (224, 224), dtype=np.uint8) # More blue
        img = Image.fromarray(fake_img_array)
        img.save(os.path.join(fake_dir, f"dummy_fake_{i}.jpg"))
        
    print("Successfully generated 50 Real and 50 AI dummy images!")
    print("\nNext steps:")
    print("1. Run `python train_image.py` to train the deep learning model on these images.")
    print("2. Once it finishes, start your Flask backend `python run.py`.")
    print("="*60)

if __name__ == "__main__":
    generate_dummy_dataset()
