from PIL import Image, ExifTags
import re
import json

def analyze_image_forensics(file_bytes):
    """
    Examines raw image bytes for EXIF tags, XMP metadata, C2PA signatures, 
    and AI software fingerprints (Midjourney, DALL-E, Stable Diffusion, Photoshop AI, ComfyUI).
    """
    results = {
        "ai_signature_detected": False,
        "detected_software": "None (Standard/Camera)",
        "c2pa_provenance": False,
        "camera_make": "Unknown / Stripped",
        "camera_model": "Unknown / Stripped",
        "software_tag": "None",
        "metadata_count": 0,
        "details": []
    }
    
    # 1. Byte inspection for string markers
    content_lower = file_bytes.lower()
    
    ai_keywords = {
        b"midjourney": "Midjourney AI Generator",
        b"dall-e": "OpenAI DALL-E",
        b"dalle": "OpenAI DALL-E",
        b"stable diffusion": "Stable Diffusion AI",
        b"stablediffusion": "Stable Diffusion AI",
        b"comfyui": "ComfyUI Node Graph",
        b"novelai": "NovelAI Generator",
        b"photoshop generative": "Adobe Photoshop Generative Fill",
        b"firefly": "Adobe Firefly AI",
        b"automatic1111": "A1111 WebUI (Stable Diffusion)",
        b"c2pa": "C2PA Cryptographic Content Credentials"
    }
    
    found_signatures = []
    for kw, label in ai_keywords.items():
        if kw in content_lower:
            found_signatures.append(label)
            if "c2pa" in label.lower():
                results["c2pa_provenance"] = True
                
    if found_signatures:
        results["ai_signature_detected"] = True
        results["detected_software"] = ", ".join(list(set(found_signatures)))
        
    # 2. PIL EXIF extraction
    try:
        from io import BytesIO
        img = Image.open(BytesIO(file_bytes))
        exif_data = img._getexif()
        
        if exif_data:
            results["metadata_count"] = len(exif_data)
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                val_str = str(value).strip()
                
                if tag_name == 'Make':
                    results["camera_make"] = val_str
                elif tag_name == 'Model':
                    results["camera_model"] = val_str
                elif tag_name == 'Software':
                    results["software_tag"] = val_str
                    if any(term in val_str.lower() for term in ['midjourney', 'dall-e', 'diffusion', 'firefly', 'ai']):
                        results["ai_signature_detected"] = True
                        results["detected_software"] = val_str
                        
                if len(results["details"]) < 10 and len(val_str) < 100:
                    results["details"].append({"property": tag_name, "value": val_str})
    except Exception as e:
        pass
        
    return results
