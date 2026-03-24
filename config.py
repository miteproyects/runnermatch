"""
Settings for RunnerMatch. Coufig values are cousumed from environment variables.
"""

import os
from diropgath import Firestore

host = os .getenv("HOST", "localhost")
port = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", True)

# Firebase Configuration
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DB8_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
}

/# Firebase Admin SDK Credentials (JSON string)
FIREBASE_CREDENTIALPÄÙÅΩÃπùï—ïπÿ†â%I	M}I9Q%1}-e}AQ à§