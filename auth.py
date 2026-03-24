"""
RunnerMatch - Firebase Authentication Module
Handles sign-up, login, password reset, and session management.
"""

import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import config

# =============================================================================
# FIREBASE INITIALIZATION
# =============================================================================

def init_firebase():
    """Initialize Firebase Admin SDK (once)."""
    if not firebase_admin._apps:
        if config.FIREBASE_CREDENTIALS:
            cred = credentials.Certificate(config.FIREBASE_CREDENTIALS)
            firebase_admin.initialize_app(cred, {
                "storageBucket": config.FIREBASE_STORAGE_BUCKET
            })
        else:
            st.warning("Firebase credentials not configured.")


def get_pyrebase_app():
    """Get Pyrebase client for client-side auth (login, signup)."""
    import pyrebase
    if config.FIREBASE_CONFIG:
        return pyrebase.initialize_app(config.FIREBASE_CONFIG)
    return None


# =============================================================================
# AUTHENTICATION FUNCTIONS
# =============================================================================

def sign_up(email: str, password: str) -> dict:
    """
    Create a new user with Firebase Authentication.
    Returns: {"success": True, "uid": "...", "email": "..."} or {"success": False, "error": "..."}
    """
    try:
        pb = get_pyrebase_app()
        if not pb:
            return {"success": False, "error": "Firebase not configured"}

        auth_client = pb.auth()
        user = auth_client.create_user_with_email_and_password(email, password)

        # Send email verification
        auth_client.send_email_verification(user["idToken"])

        return {
            "success": True,
            "uid": user["localId"],
            "email": email,
            "id_token": user["idToken"],
            "refresh_token": user["refreshToken"],
        }
    except Exception as e:
        error_msg = str(e)
        if "EMAIL_EXISTS" in error_msg:
            return {"success": False, "error": "email_exists"}
        elif "WEAK_PASSWORD" in error_msg:
            return {"success": False, "error": "weak_password"}
        elif "INVALID_EMAIL" in error_msg:
            return {"success": False, "error": "invalid_email"}
        return {"success": False, "error": error_msg}


def sign_in(email: str, password: str) -> dict:
    """
    Sign in an existing user.
    Returns: {"success": True, "uid": "...", ...} or {"success": False, "error": "..."}
    """
    try:
        pb = get_pyrebase_app()
        if not pb:
            return {"success": False, "error": "Firebase not configured"}

        auth_client = pb.auth()
        user = auth_client.sign_in_with_email_and_password(email, password)

        return {
            "success": True,
            "uid": user["localId"],
            "email": email,
            "id_token": user["idToken"],
            "refresh_token": user["refreshToken"],
        }
    except Exception as e:
        error_msg = str(e)
        if "INVALID_LOGIN_CREDENTIALS" in error_msg or "INVALID_PASSWORD" in error_msg:
            return {"success": False, "error": "invalid_credentials"}
        elif "USER_DISABLED" in error_msg:
            return {"success": False, "error": "user_disabled"}
        elif "TOO_MANY_ATTEMPTS" in error_msg:
            return {"success": False, "error": "too_many_attempts"}
        return {"success": False, "error": error_msg}


def reset_password(email: str) -> dict:
    """Send password reset email."""
    try:
        pb = get_pyrebase_app()
        if not pb:
            return {"success": False, "error": "Firebase not configured"}

        auth_client = pb.auth()
        auth_client.send_password_reset_email(email)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def verify_token(id_token: str) -> dict:
    """Verify a Firebase ID token (server-side)."""
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return {"success": True, "uid": decoded["uid"], "email": decoded.get("email")}
    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

def init_session_state():
    """Initialize authentication session state."""
    defaults = {
        "authenticated": False,
        "user_uid": None,
        "user_email": None,
        "user_role": "unverified",
        "user_db_id": None,
        "id_token": None,
        "refresh_token": None,
        "language": config.DEFAULT_LANGUAGE,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_authenticated(uid: str, email: str, id_token: str, refresh_token: str,
                      role: str = "unverified", db_id: int = None):
    """Set session as authenticated."""
    st.session_state.authenticated = True
    st.session_state.user_uid = uid
    st.session_state.user_email = email
    st.session_state.user_role = role
    st.session_state.user_db_id = db_id
    st.session_state.id_token = id_token
    st.session_state.refresh_token = refresh_token


def logout():
    """Clear session state."""
    for key in ["authenticated", "user_uid", "user_email", "user_role",
                "user_db_id", "id_token", "refresh_token"]:
        if key in st.session_state:
            del st.session_state[key]
    init_session_state()


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def is_verified() -> bool:
    return st.session_state.get("user_role") in ("verified", "admin")


def is_admin() -> bool:
    return st.session_state.get("user_role") == "admin"


def require_auth():
    """Redirect to login if not authenticated. Call at top of protected pages."""
    if not is_authenticated():
        st.session_state.page = "login"
        st.rerun()


def require_verified():
    """Redirect to verification if not verified."""
    require_auth()
    if not is_verified():
        st.session_state.page = "verify"
        st.rerun()
