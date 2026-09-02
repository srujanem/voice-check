import subprocess
import sys

print("\nStarting PyTorch ViT Training (with 13 new complex AI images)...")
sys.stdout.flush()
subprocess.run(["python", "-u", "train_vit_gpu.py"])

print("\nStarting TensorFlow Training...")
sys.stdout.flush()
subprocess.run(["python", "-u", "train_image_advanced.py"])

print("\nALL UPGRADES COMPLETE!")
sys.stdout.flush()
