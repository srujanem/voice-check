import os
import json
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file (local dev only)
load_dotenv()

# ── Firebase credentials from env var (Render / cloud deployment) ──────────
firebase_creds_json = os.environ.get("FIREBASE_CREDENTIALS")
if firebase_creds_json and not os.path.exists("serviceAccountKey.json"):
    try:
        creds = json.loads(firebase_creds_json)
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=".json", mode="w", dir="."
        )
        json.dump(creds, tmp)
        tmp.close()
        os.rename(tmp.name, "serviceAccountKey.json")
        print("Firebase credentials written from environment variable.")
    except Exception as e:
        print(f"Could not write Firebase credentials: {e}")

from backend import create_app

app = create_app()

port = int(os.environ.get("PORT", 5000))
host = os.environ.get("HOST", "0.0.0.0")
threads = int(os.environ.get("WAITRESS_THREADS", 4))

print(f"Starting AuthGuard on {host}:{port} ...")

from waitress import serve
serve(app, host=host, port=port, threads=threads)
