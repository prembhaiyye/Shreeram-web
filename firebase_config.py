import firebase_admin
from firebase_admin import credentials, firestore
import os

db = None

def initialize_firebase():
    global db
    if not firebase_admin._apps:
        cred_path = 'serviceAccountKey.json'
        
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("✅ Firebase initialized successfully.")
        else:
            print("WARNING: serviceAccountKey.json not found. Firebase features will not work.")
            db = None # Application should handle this gracefully (e.g. show setup page)
    else:
        db = firestore.client()

    return db

# Initialize on import so 'db' is available
initialize_firebase()
