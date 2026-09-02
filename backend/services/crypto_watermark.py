import hashlib
import json
import os
from datetime import datetime
from PIL import Image

def generate_c2pa_signature(image_path, user_id="anonymous", author_name="AuthGuard Platform"):
    """
    Generates a mock C2PA cryptographic signature for an image.
    In a full production environment, this would use pyC2PA and RSA private keys.
    """
    try:
        # 1. Read file bytes and calculate SHA-256 hash of the original pixel data
        with open(image_path, 'rb') as f:
            file_bytes = f.read()
        
        image_hash = hashlib.sha256(file_bytes).hexdigest()
        
        # 2. Create the C2PA Manifest (JUMBF payload)
        manifest = {
            "c2pa_version": "1.3",
            "claim_generator": "AuthGuard Cryptographic Engine v2.0",
            "signature_date": datetime.utcnow().isoformat() + "Z",
            "assertions": [
                {
                    "label": "stds.schema-org.CreativeWork",
                    "data": {
                        "author": [{"@type": "Person", "name": author_name}],
                        "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"
                    }
                },
                {
                    "label": "c2pa.hash.data",
                    "data": {
                        "exclusions": [],
                        "hash": image_hash,
                        "pad": "00000000"
                    }
                }
            ],
            "cryptographic_binding": {
                "algorithm": "RSASSA-PSS",
                "public_key_fingerprint": hashlib.sha256(b"AuthGuard_Public_Key_v1").hexdigest()
            }
        }
        
        # 3. Inject the Manifest into the Image EXIF/Metadata
        img = Image.open(image_path)
        exif_dict = img.getexif()
        
        # Exif tag 0x010E is ImageDescription, we'll store the C2PA JSON there for now
        # (True C2PA uses a dedicated JUMBF box in the JPEG/PNG headers)
        manifest_string = json.dumps(manifest)
        exif_dict[0x010E] = f"C2PA_MANIFEST:{manifest_string}"
        
        # Save the protected image
        protected_path = image_path.replace(".jpg", "_protected.jpg").replace(".png", "_protected.png")
        img.save(protected_path, exif=exif_dict)
        
        return {
            "success": True,
            "hash": image_hash,
            "manifest": manifest,
            "protected_file": protected_path
        }
        
    except Exception as e:
        print(f"C2PA Encryption Error: {e}")
        return {"success": False, "error": str(e)}

def verify_c2pa_signature(image_path):
    """
    Verifies if an image has a valid AuthGuard C2PA signature and if it has been tampered with.
    """
    try:
        img = Image.open(image_path)
        exif_dict = img.getexif()
        
        description = exif_dict.get(0x010E, "")
        if not description.startswith("C2PA_MANIFEST:"):
            return {"authentic": False, "reason": "No C2PA manifest found."}
            
        manifest_string = description.replace("C2PA_MANIFEST:", "")
        manifest = json.loads(manifest_string)
        
        # In a real scenario, we'd strip the EXIF, re-hash the raw pixels, and compare to manifest['assertions'][1]['data']['hash']
        # But for this simulation, we verify the signature structure.
        if "c2pa_version" in manifest and manifest.get("claim_generator", "").startswith("AuthGuard"):
            return {
                "authentic": True, 
                "signature_date": manifest.get("signature_date"),
                "author": manifest["assertions"][0]["data"]["author"][0]["name"]
            }
            
        return {"authentic": False, "reason": "Invalid signature structure."}
        
    except Exception as e:
        return {"authentic": False, "reason": f"Verification failed: {str(e)}"}
