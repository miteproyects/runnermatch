"""
RunnerMatch - Authentication Module
Handles sign-up, login, password reset, and session management.
Supports Firebase Auth (primary) with DB-based bcrypt fallback.
"""

import uuid
import streamlit as st
import bcrypt
import config

# =============================================================================
# FIREBASE INITIALIZATION
# =============================================================================

_firebase_available = False

def init_firebase():
    """Initialize Firebase Admin SDK (once)."""
    global _firebase_available
    if config.FIREBASE_CREDENTIALS:
        try:
            import firebase_admin
            from firebase_admin import credentials
            if not firebase_admin._apps:
                cred = credentials.Certificate(config.FIREBASE_CREDENTIALS)
                firebase_admin.initialize_app(cred, {
                    "storageBucket": config.FIREBASE_STORAGE_BUCKET
                })
            _firebase_available = True
        except Exception as e:
            st.warning(f"Firebase init error: {e}")
            _firebase_available = False
    else:
        _firebase_available = False


def _use_firebase():
    """Check if Firebase auth is available."""
    return _firebase_available and bool(config.FIREBASE_CONFIG)


def get_pyrebase_app():
    """Get Pyrebase client for client-side auth (login, signup)."""
    if not _use_firebase():
        return None
    try:
        import pyrebase
        return pyrebase.initialize_app(config.FIREBASE_CONFIG)
    except Exception:
        return None


# =============================================================================
# DB-BASED AUTH FALLBACK (bcrypt)
# =============================================================================

def _hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _check_password(password: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def _db_sign_up(email: str, password: str) -> dict:
    """Create a new user using DB-based auth."""
    from database import get_db, User
    try:
        db = next(get_db())
        existing = db.query(User).filter_by(email=email).first()
        if existing:
            db.close()
            return {"success": False, "error": "email_exists"}

        uid = f"local_{uuid.uuid4().hex[:24]}"
        pw_hash = _hash_password(password)
        new_user = User(
            firebase_uid=uid,
            email=email,
            password_hash=pw_hash,
            language=st.session_state.get("language", "es"),
        )
        db.add(new_user)
        db.commit()
        db_id = new_user.id
        db.close()

        return {
            "success": True,
            "uid": uid,
            "email": email,
            "id_token": f"local_token_{uid}",
            "refresh_token": f"local_refresh_{uid}",
            "db_id": db_id,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _db_sign_in(email: str, password: str) -> dict:
    """Sign in using DB-based auth."""
    from database import get_db, User
    try:
        db = next(get_db())
        user = db.query(User).filter_by(email=email).first()
        if not user:
            db.close()
            return {"success": False, "error": "invalid_credentials"}

        if not user.password_hash:
            db.close()
            return {"success": False, "error": "invalid_credentials"}

        if not _check_password(password, user.password_hash):
            db.close()
            return {"success": False, "error": "invalid_credentials"}

        uid = user.firebase_uid or f"local_{user.id}"
        db_id = user.id
        role = user.role
        lang = user.language
        db.close()

        return {
            "success": True,
            "uid": uid,
            "email": email,
            "id_token": f"local_token_{uid}",
            "refresh_token": f"local_refresh_{uid}",
            "db_id": db_id,
            "role": role,
            "language": lang,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# AUTHENTICATION FUNCTIONS (unified: Firebase or DB fallback)
# =============================================================================

def sign_up(email: str, password: str) -> dict:
    """
    Create a new user. Uses Firebase if configured, otherwise DB-based auth.
    Returns: {"success": True, "uid": "...", "email": "..."} or {"success": False, "error": "..."}
    """
    if _use_firebase():
        try:
            pb = get_pyrebase_app()
            if not pb:
                return _db_sign_up(email, password)

            auth_client = pb.auth()
            user = auth_client.create_user_with_email_and_password(email, password)

            try:
                auth_client.send_email_verification(user["idToken"])
            except Exception:
                pass

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
    else:
        return _db_sign_up(email, password)


def sign_in(email: str, password: str) -> dict:
    """
    Sign in an existing user. Uses Firebase if configured, otherwise DB-based auth.
    """
    if _use_firebase():
        try:
            pb = get_pyrebase_app()
            if not pb:
                return _db_sign_in(email, password)

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
    else:
        return _db_sign_in(email, password)


def reset_password(email: str) -> dict:
    """Send password reset email (Firebase only)."""
    if _use_firebase():
        try:
            pb = get_pyrebase_app()
            if not pb:
                return {"success": False, "error": "Not available in local auth mode"}
            auth_client = pb.auth()
            auth_client.send_password_reset_email(email)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        return {"success": False, "error": "Password reset requires Firebase configuration"}


def verify_token(id_token: str) -> dict:
    """Verify a Firebase ID token (server-side)."""
    if id_token and id_token.startswith("local_token_"):
        uid = id_token.replace("local_token_", "")
        return {"success": True, "uid": uid}
    try:
        from firebase_admin import auth as firebase_auth
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
