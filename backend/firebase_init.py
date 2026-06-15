import firebase_admin
from firebase_admin import credentials, firestore
import os

def init_firebase():
    if not firebase_admin._apps:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        key_path = os.path.join(base_dir, 'serviceAccountKey.json')
        
        try:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin Initialized Successfully")
        except Exception as e:
            print(f"WARNING: Could not initialize Firebase Admin SDK. Did you put serviceAccountKey.json in the root folder? Error: {e}")

def get_db():
    return firestore.client()
