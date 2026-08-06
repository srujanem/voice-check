"""
download_models.py — Run before gunicorn starts on Render.

Models are stored on Google Drive (or any public URL).
Set these environment variables on Render:
  MODEL_VOICE_URL   = direct download URL for model.keras
  MODEL_IMAGE_URL   = direct download URL for model_image.keras
  MODEL_SCALER_URL  = direct download URL for scaler.pkl
  MODEL_TEXT_URL    = direct download URL for text_model.pkl
  MODEL_VECTZ_URL   = direct download URL for text_vectorizer.pkl

If a model file already exists (from a previous deploy), it is skipped.
"""

import os
import sys
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODELS = [
    ("MODEL_VOICE_URL",  "model.keras"),
    ("MODEL_SCALER_URL", "scaler.pkl"),
    ("MODEL_IMAGE_URL",  "model_image.keras"),
    ("MODEL_TEXT_URL",   "text_model.pkl"),
    ("MODEL_VECTZ_URL",  "text_vectorizer.pkl"),
]

def download(url: str, dest: str):
    print(f"  Downloading → {os.path.basename(dest)} ...", flush=True)
    resp = requests.get(url, stream=True, timeout=300)
    resp.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    size_mb = os.path.getsize(dest) / 1024 / 1024
    print(f"  ✅ {os.path.basename(dest)} saved ({size_mb:.1f} MB)", flush=True)

def main():
    print("=== Model Download Check ===", flush=True)
    all_ok = True
    for env_var, filename in MODELS:
        dest = os.path.join(BASE_DIR, filename)
        if os.path.exists(dest):
            print(f"  ✓ {filename} already exists, skipping.", flush=True)
            continue
        url = os.environ.get(env_var)
        if not url:
            print(f"  ⚠️  {env_var} not set — {filename} will not be available.", flush=True)
            all_ok = False
            continue
        try:
            download(url, dest)
        except Exception as e:
            print(f"  ❌ Failed to download {filename}: {e}", flush=True)
            all_ok = False
    print("=== Done ===", flush=True)
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
