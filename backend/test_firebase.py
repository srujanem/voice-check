import firebase_admin
from firebase_admin import credentials, firestore

try:
    # Attempt to initialize with default credentials
    default_app = firebase_admin.initialize_app()
    db = firestore.client()
    print("SUCCESS: Initialized Firebase Admin SDK")
except Exception as e:
    print(f"FAILED: {e}")
