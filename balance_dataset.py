import os
import glob
import random
import shutil

real_dir = r'D:\voice-check\voice-check\dataset_image\real'
fake_dir = r'D:\voice-check\voice-check\dataset_image\fake'
source_dir = r'E:\family pics real'

real_count = len([name for name in os.listdir(real_dir) if os.path.isfile(os.path.join(real_dir, name))])
fake_count = len([name for name in os.listdir(fake_dir) if os.path.isfile(os.path.join(fake_dir, name))])

print(f'Current Real: {real_count}')
print(f'Current Fake: {fake_count}')

if fake_count > real_count:
    needed = fake_count - real_count
    print(f'Need {needed} more real images.')
    
    all_source_pics = glob.glob(os.path.join(source_dir, '**', '*.*'), recursive=True)
    all_source_pics = [p for p in all_source_pics if p.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if len(all_source_pics) >= needed:
        selected_pics = random.sample(all_source_pics, needed)
    else:
        print('Not enough source pictures. Using all available.')
        selected_pics = all_source_pics
        
    for i, pic_path in enumerate(selected_pics):
        ext = os.path.splitext(pic_path)[1]
        dest_name = f'family_added_{i}_{random.randint(1000, 9999)}{ext}'
        dest_path = os.path.join(real_dir, dest_name)
        shutil.copy2(pic_path, dest_path)
        
    new_real_count = len([name for name in os.listdir(real_dir) if os.path.isfile(os.path.join(real_dir, name))])
    print(f'Successfully added images. New Real Count: {new_real_count}')
else:
    print('Dataset is already balanced or has more real images than fake.')
