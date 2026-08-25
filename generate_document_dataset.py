import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# Configuration
NUM_SAMPLES = 500  # Will generate 500 Real and 500 Fake
OUTPUT_DIR = "dataset_document"
REAL_DIR = os.path.join(OUTPUT_DIR, "real")
FAKE_DIR = os.path.join(OUTPUT_DIR, "fake")

# Create directories
os.makedirs(REAL_DIR, exist_ok=True)
os.makedirs(FAKE_DIR, exist_ok=True)

def generate_paper_texture(width=800, height=1000):
    """Generates a blank image that looks like scanned paper with slight noise."""
    # Base white paper
    base = np.ones((height, width, 3), dtype=np.uint8) * 245
    
    # Add random Gaussian noise to simulate scanner grain
    noise = np.random.normal(0, 5, (height, width, 3)).astype(np.uint8)
    paper = np.clip(base + noise, 0, 255).astype(np.uint8)
    
    img = Image.fromarray(paper)
    return img

def create_authentic_document(doc_id):
    """Generates an authentic-looking synthetic invoice or certificate."""
    img = generate_paper_texture()
    draw = ImageDraw.Draw(img)
    
    # Use default font
    font = ImageFont.load_default()
    
    # Draw Header (Company Logo Box)
    draw.rectangle([50, 50, 200, 150], outline="black", width=2)
    draw.text((80, 90), "COMPANY LOGO", fill="black", font=font)
    
    # Draw Title
    draw.text((300, 80), "OFFICIAL INVOICE", fill="black", font=font)
    draw.text((300, 100), f"Invoice #: 100{doc_id:04d}", fill="black", font=font)
    draw.text((300, 120), f"Date: 2026-08-{random.randint(10, 28)}", fill="black", font=font)
    
    # Draw Lines and Items
    y_offset = 250
    draw.line([(50, y_offset), (750, y_offset)], fill="black", width=2)
    
    for i in range(3):
        y_offset += 40
        draw.text((50, y_offset), f"Service Item {i+1}", fill="black", font=font)
        price = random.randint(100, 900)
        draw.text((650, y_offset), f"${price}.00", fill="black", font=font)
    
    y_offset += 60
    draw.line([(50, y_offset), (750, y_offset)], fill="black", width=2)
    
    # Draw Total Amount
    y_offset += 20
    total = random.randint(1000, 5000)
    draw.text((550, y_offset), "TOTAL AMOUNT:", fill="black", font=font)
    
    # We will record the bounding box of the total amount so we can specifically target it for forgery!
    total_bbox = [650, y_offset, 750, y_offset + 20]
    draw.text((650, y_offset), f"${total}.00", fill="black", font=font)
    
    # Draw Signature Line
    draw.line([(50, 850), (250, 850)], fill="black", width=1)
    draw.text((50, 860), "Authorized Signature", fill="black", font=font)
    
    # Simulate scanning artifact (slight blur and contrast reduction)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(0.9)
    
    return img, total_bbox

def apply_forgery(img, target_bbox):
    """Applies digital manipulation to simulate a forged document."""
    forgery_type = random.choice(["copy_move", "text_alteration", "splicing"])
    
    # Convert to RGB if not already
    forged_img = img.copy().convert("RGB")
    draw = ImageDraw.Draw(forged_img)
    font = ImageFont.load_default()
    
    if forgery_type == "copy_move":
        # Copy a blank piece of paper from the bottom and paste it over the Total Amount
        # This simulates erasing the amount
        blank_patch = forged_img.crop((50, 900, 150, 920))
        forged_img.paste(blank_patch, (target_bbox[0], target_bbox[1]))
        
        # Draw a fake new amount with a slightly misaligned Y-axis to simulate poor forgery
        fake_amount = random.randint(9000, 99999)
        draw.text((target_bbox[0] + 2, target_bbox[1] - 2), f"${fake_amount}.00", fill="black", font=font)
        
    elif forgery_type == "text_alteration":
        # Draw a pure white box over the total amount (looks unnatural compared to the grainy paper)
        draw.rectangle(target_bbox, fill="white")
        
        # Write massive fake amount
        fake_amount = random.randint(10000, 50000)
        draw.text((target_bbox[0], target_bbox[1]), f"${fake_amount}.00", fill="#111111", font=font)
        
    elif forgery_type == "splicing":
        # Simulate pasting a signature from another document
        # We'll create a small patch with a fake signature and paste it near the signature line
        sig_patch = Image.new("RGB", (150, 80), color=(255, 255, 255))
        sig_draw = ImageDraw.Draw(sig_patch)
        sig_draw.text((20, 30), "Fake Signature", fill="blue", font=font)
        
        # Compress the patch aggressively to create Error Level Analysis (ELA) anomalies
        sig_patch.save("temp_patch.jpg", quality=10)
        sig_patch = Image.open("temp_patch.jpg")
        
        # Paste it over the signature line
        forged_img.paste(sig_patch, (50, 770))
        if os.path.exists("temp_patch.jpg"):
            os.remove("temp_patch.jpg")
            
    # Save the forged image with high compression to simulate a re-saved JPEG (classic forgery footprint)
    return forged_img

print("==================================================")
print("  DOCUMENT FORGERY DATASET GENERATOR")
print("==================================================")
print(f"Generating {NUM_SAMPLES} authentic and {NUM_SAMPLES} forged documents...")

for i in range(NUM_SAMPLES):
    if i % 50 == 0 and i > 0:
        print(f"[{i}/{NUM_SAMPLES}] documents generated...")
        
    # 1. Generate Authentic Document
    real_doc, target_bbox = create_authentic_document(i)
    real_path = os.path.join(REAL_DIR, f"doc_{i:04d}.jpg")
    real_doc.save(real_path, quality=95)  # High quality original
    
    # 2. Generate Forged/Tampered Document
    fake_doc = apply_forgery(real_doc, target_bbox)
    fake_path = os.path.join(FAKE_DIR, f"doc_{i:04d}.jpg")
    fake_doc.save(fake_path, quality=75)  # Re-saved at lower quality due to manipulation

print("==================================================")
print(f"SUCCESS! Dataset created at: {OUTPUT_DIR}")
print(f"Real documents: {len(os.listdir(REAL_DIR))}")
print(f"Fake documents: {len(os.listdir(FAKE_DIR))}")
print("==================================================")
