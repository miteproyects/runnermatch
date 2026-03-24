"""
RunnerMatch - Configuration Module
Centralized configuration management via environment variables.
"""

import os
import json

# =============================================================================
# DATABASE
# =============================================================================
DATABASE_URL = os.environ.get("DATABASE_URL", "")
# Railway uses postgresql:// but SQLAlchemy needs postgresql+psycopg2://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+psycopg2" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# =============================================================================
# APPLICATION
# =============================================================================
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
APP_URL = os.environ.get("APP_URL", "http://localhost:8080")
APP_PORT = int(os.environ.get("APP_PORT", "8080"))
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# =============================================================================
# FIREBASE
# =============================================================================
FIREBASE_CONFIG = json.loads(os.environ.get("FIREBASE_CONFIG", "{}"))
FIREBASE_CREDENTIALS = json.loads(os.environ.get("FIREBASE_CREDENTIALS", "{}"))
FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET", "")

# =============================================================================
# GMAIL NOTIFICATIONS
# =============================================================================
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

# =============================================================================
# APP SETTINGS
# =============================================================================
MAX_PHOTOS = 6
MAX_PHOTO_SIZE_MB = 5
SESSION_TIMEOUT_MINUTES = 60
SUPPORTED_LANGUAGES = ["es", "en"]
DEFAULT_LANGUAGE = "es"

# Race verification fuzzy match threshold (0-100, higher = stricter)
FUZZY_MATCH_THRESHOLD = 80
