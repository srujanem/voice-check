import os
import shutil
import uuid
import glob

# Paths
ai_src_dir = r'D:\images'
real_src_dirs = [r'E:\family pics real', r'E:\srujan phone pics']

ai_dest_dir = r'D:\voice-check\voice-check\dataset_image\fake'
real_dest_dir = r'D:\voice-check\voice-check\dataset_image\real'

os.makedirs(ai_dest_dir, exist_ok=True)
os.makedirs(real_dest_dir, exist_ok=True)

image_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}

def process_files(src_dir, dest_dir, action='copy'):
    count = 0
    if not os.path.exists(src_dir):
        return count
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in image_exts:
                src_path = os.path.join(root, file)
                
                # Create a unique filename to avoid overlapping
                new_filename = f"{uuid.uuid4().hex}{ext}"
                dest_path = os.path.join(dest_dir, new_filename)
                
                try:
                    if action == 'copy':
                        shutil.copy2(src_path, dest_path)
                    elif action == 'move':
                        shutil.move(src_path, dest_path)
                    count += 1
                except Exception as e:
                    print(f"Error processing {src_path}: {e}")
                    
    return count

print("Starting migration...")
ai_moved = process_files(ai_src_dir, ai_dest_dir, action='move')
print(f"Moved {ai_moved} AI images from D:\\images to fake dataset.")

real_copied = 0
for r_dir in real_src_dirs:
    real_copied += process_files(r_dir, real_dest_dir, action='copy')
print(f"Copied {real_copied} Real images from E:\\ to real dataset.")
