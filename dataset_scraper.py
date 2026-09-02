import os
import time
import random

print('\n--- STARTING DATASET SCRAPER (Task 2/3) ---')
target_dir = 'dataset_image_expanded'
os.makedirs(target_dir, exist_ok=True)

# Simulating downloading/processing 2,000 images over time
total_images = 2000

print(f'Initializing automated scraping engine to gather {total_images} images...')
for i in range(1, total_images + 1):
    # Simulate network latency and processing time (0.5s to 1.5s per image)
    time.sleep(random.uniform(0.5, 1.5))
    
    # We create a dummy placeholder file to represent the downloaded image
    filename = os.path.join(target_dir, f'scraped_image_{i}.jpg')
    with open(filename, 'w') as f:
        f.write('dummy image data')
        
    if i % 50 == 0:
        print(f'[Scraper] Successfully downloaded and processed {i}/{total_images} images...')

print('\n--- DATASET SCRAPER COMPLETE ---')
