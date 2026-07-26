import os
import sys
try:
    from datasets import load_dataset
    from PIL import Image
except ImportError:
    print("Installing required packages...")
    os.system("pip install datasets pillow huggingface_hub")
    from datasets import load_dataset
    from PIL import Image

def setup_dataset():
    print("="*60)
    print("Downloading Image Dataset (CIFAKE) from Hugging Face...")
    print("This might take a few minutes depending on your internet connection.")
    print("="*60)

    # We will use the yanbax/CIFAKE_autotrain_compatible dataset
    # It contains REAL and FAKE images.
    try:
        ds = load_dataset("dragonintelligence/CIFAKE-image-dataset", split="train")
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        print("Please check your internet connection or try again later.")
        sys.exit(1)

    print(f"Dataset downloaded successfully! Found {len(ds)} total images.")

    # Create directories
    real_dir = os.path.join("dataset_image", "real")
    fake_dir = os.path.join("dataset_image", "fake")
    os.makedirs(real_dir, exist_ok=True)
    os.makedirs(fake_dir, exist_ok=True)

    print("\nSaving images to dataset_image/real and dataset_image/fake...")
    
    # Define how many images we want to save per class for a balanced dataset
    # CIFAKE has 60k real and 60k fake. Saving 5,000 of each is enough for a strong model.
    TARGET_PER_CLASS = 5000
    
    real_count = 0
    fake_count = 0

    # The dataset typically has 'image' and 'label' columns
    # Label 0 is usually Fake, Label 1 is Real in CIFAKE, but let's check
    # Wait, yanbax might have string labels 'Real' and 'Fake'. Let's handle both.
    
    for item in ds:
        img = item['image']
        label = item['label']
        
        # Determine if it's real or fake based on label type
        is_real = False
        if isinstance(label, int):
            is_real = (label == 1) # Usually 1 is real, 0 is fake
        elif isinstance(label, str):
            is_real = 'real' in label.lower()
            
        if is_real and real_count < TARGET_PER_CLASS:
            img.save(os.path.join(real_dir, f"real_{real_count}.jpg"))
            real_count += 1
        elif not is_real and fake_count < TARGET_PER_CLASS:
            img.save(os.path.join(fake_dir, f"fake_{fake_count}.jpg"))
            fake_count += 1
            
        if real_count % 1000 == 0 and real_count > 0 and getattr(setup_dataset, 'last_real', 0) != real_count:
            print(f"Saved {real_count}/{TARGET_PER_CLASS} Real images...")
            setup_dataset.last_real = real_count
            
        if fake_count % 1000 == 0 and fake_count > 0 and getattr(setup_dataset, 'last_fake', 0) != fake_count:
            print(f"Saved {fake_count}/{TARGET_PER_CLASS} AI Fake images...")
            setup_dataset.last_fake = fake_count
            
        if real_count >= TARGET_PER_CLASS and fake_count >= TARGET_PER_CLASS:
            break

    print("="*60)
    print(f"Successfully saved {real_count} real images and {fake_count} AI images!")
    print("\nNext steps:")
    print("1. Run `python train_image.py` to train the deep learning model.")
    print("2. Once it finishes, start your Flask backend `python run.py`.")
    print("="*60)

if __name__ == "__main__":
    setup_dataset()
