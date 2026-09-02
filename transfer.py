import os, glob, hashlib, shutil

def get_hash(filepath):
    sz = os.path.getsize(filepath)
    with open(filepath, 'rb') as f:
        head = f.read(32768)
        f.seek(max(0, sz - 32768))
        tail = f.read(32768)
    return hashlib.md5(str(sz).encode() + head + tail).hexdigest()

dest_dir = 'D:/voice-check/voice-check/dataset_image/real'
custom_dir = 'D:/voice-check/voice-check/dataset_custom/real'
os.makedirs(dest_dir, exist_ok=True)
os.makedirs(custom_dir, exist_ok=True)

existing_hashes = set()
for d in [dest_dir, custom_dir]:
    for f in glob.glob(d + '/*'):
        if os.path.isfile(f):
            try:
                existing_hashes.add(get_hash(f))
            except: pass

print(f"Indexed {len(existing_hashes)} existing real images.")

src_files = glob.glob('D:/images/*')
print(f"Total files in D:/images: {len(src_files)}")

moved_count = 0
skipped_overlap = 0

for f in src_files:
    if os.path.isfile(f):
        h = get_hash(f)
        if h in existing_hashes:
            skipped_overlap += 1
            os.remove(f)
        else:
            existing_hashes.add(h)
            fname = os.path.basename(f)
            dest_path = os.path.join(dest_dir, fname)
            if os.path.exists(dest_path):
                name, ext = os.path.splitext(fname)
                dest_path = os.path.join(dest_dir, f"{name}_new_{moved_count}{ext}")
            shutil.move(f, dest_path)
            shutil.copy2(dest_path, os.path.join(custom_dir, os.path.basename(dest_path)))
            moved_count += 1

print(f"SUCCESS: Cut-pasted {moved_count} new unique images into dataset_image/real and dataset_custom/real.")
print(f"Duplicates/Overlaps skipped and cleaned: {skipped_overlap}")
print(f"Remaining in D:/images: {len(glob.glob('D:/images/*'))}")
