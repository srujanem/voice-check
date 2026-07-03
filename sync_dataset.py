import os
import sys
import base64
import requests

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.routes.external_db_routes import _get_db

def ensure_dirs():
    os.makedirs("dataset/human", exist_ok=True)
    os.makedirs("dataset/ai", exist_ok=True)
    os.makedirs("dataset_image/real", exist_ok=True)
    os.makedirs("dataset_image/fake", exist_ok=True)

def sync_data():
    db_instance = _get_db()
    if not db_instance.is_configured():
        return False, "External DB is not configured. Please go to the Login page and connect to the database first!"

    ensure_dirs()
    log_output = []

    try:
        # We assume the friend's database has these collections:
        # 'audio_dataset' and 'image_dataset'
        
        # 1. Sync Audio
        audio_docs = db_instance.list_documents("audio_dataset")
        if audio_docs and isinstance(audio_docs, list):
            log_output.append(f"Found {len(audio_docs)} audio documents.")
            for i, doc in enumerate(audio_docs):
                label = doc.get("label", "ai").lower() # 'human' or 'ai'
                folder = "dataset/human" if label == "human" else "dataset/ai"
                
                # If they store base64 data
                if "base64_data" in doc:
                    try:
                        ext = doc.get("extension", ".wav")
                        filename = doc.get("filename", f"ext_sync_{i}{ext}")
                        filepath = os.path.join(folder, filename)
                        
                        audio_data = base64.b64decode(doc["base64_data"])
                        with open(filepath, "wb") as f:
                            f.write(audio_data)
                        log_output.append(f"Saved {filepath}")
                    except Exception as e:
                        log_output.append(f"Failed to decode audio doc {i}: {e}")
        
        # 2. Sync Images
        image_docs = db_instance.list_documents("image_dataset")
        if image_docs and isinstance(image_docs, list):
            log_output.append(f"Found {len(image_docs)} image documents.")
            for i, doc in enumerate(image_docs):
                label = doc.get("label", "fake").lower() # 'real' or 'fake'
                folder = "dataset_image/real" if label == "real" else "dataset_image/fake"
                
                if "base64_data" in doc:
                    try:
                        ext = doc.get("extension", ".jpg")
                        filename = doc.get("filename", f"ext_sync_{i}{ext}")
                        filepath = os.path.join(folder, filename)
                        
                        img_data = base64.b64decode(doc["base64_data"])
                        with open(filepath, "wb") as f:
                            f.write(img_data)
                        log_output.append(f"Saved {filepath}")
                    except Exception as e:
                        log_output.append(f"Failed to decode image doc {i}: {e}")

        return True, "\n".join(log_output)
    except Exception as e:
        return False, f"Sync error: {str(e)}"

if __name__ == "__main__":
    success, logs = sync_data()
    print("Success:" if success else "Error:")
    print(logs)
