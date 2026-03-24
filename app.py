"""
RunnerMatch — Dating App for Verified Runners
Main application entry point.
"""

import streamlit as st

# Page config must be first Streamlit command
st.set_page_config(
    page_title="RunnerMatch",
    page_icon="🏃",
    layout="centered",
    initial_sidebar_state="collapsed",
)

import config
from database import init_db
from auth import init_firebase, init_session_state, is_authenticated, is_verified, is_admin, logout
from i18n import t, language_selector
from chat import get_unread_count

# =============================================================================
# INITIALIZATION
# =============================================================================

init_firebase()
init_session_state()

# Initialize DB tables on first run
if "db_initialized" not in st.session_state:
    try:
        init_db()
        st.session_state.db_initialized = True
    except Exception as e:
        st.error(f"Database connection error: {e}")
        st.stop()


# =============================================================================
# CUSTOM CSS (mobile-friendly, dating app feel)
# =============================================================================

st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Mobile-friendly container */
    .block-container {
        max-width: 480px !important;
        padding: 1rem !important;
    }

    /* Rounded buttons */
    .stButton > button {
        border-radius: 24px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        transform: scale(1.02);
    }

    /* Primary button style */
    .stButton > button[kind="primary"] {
        background-color: #FF6B35;
        border-color: #FF6B35;
    }

    /* Form inputs */
    .stTextInput > div > div > input {
        border-radius: 12px;
    }

    .stSelectbox > div > div {
        border-radius: 12px;
    }

    /* Navigation bar styling */
    .nav-bar {
        display: flex;
        justify-content: space-around;
        padding: 8px 0;
        background: white;
        border-top: 1px solid #eee;
        position: sticky;
        bottom: 0;
    }

    .nav-item {
        text-align: center;
        padding: 8px 16px;
        cursor: pointer;
        color: #666;
        font-size: 0.85em;
    }

    .nav-item.active {
        color: #FF6B35;
        font-weight: bold;
    }

    /* Card styles */
    .profile-card {
        background: white;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        padding: 20px;
        margin: 10px 0;
    }

    /* Match animation */
    @keyframes matchPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    .match-popup {
        animation: matchPulse 0.5s ease-in-out;
    }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.2em;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# ROUTING & NAVIGATION
# =============================================================================

def render_navigation():
    """Render bottom navigation bar for authenticated users."""
    if not is_authenticated():
        return

    # Get unread message count
    unread = 0
    if is_verified():
        try:
            from database import get_db
            db = next(get_db())
            unread = get_unread_count(db, st.session_state.user_db_id)
            db.close()
        except Exception:
            pass

    unread_badge = f" ({unread})" if unread > 0 else ""

    st.markdown("---")
    cols = st.columns(5 if is_admin() else 4)

    current_page = st.session_state.get("page", "discover")

    with cols[0]:
        icon = "🏃" if current_page != "discover" else "🏃‍♂️"
        if st.button(f"{icon}\n{t('discover')}", use_container_width=True,
                      disabled=not is_verified(), key="nav_discover"):
            st.session_state.page = "discover"
            st.rerun()

    with cols[1]:
        if st.button(f"💬\n{t('messages')}{unread_badge}", use_container_width=True,
                      disabled=not is_verified(), key="nav_messages"):
            st.session_state.page = "messages"
            st.rerun()

    with cols[2]:
        if st.button(f"✅\n{t('verify_race')}", use_container_width=True, key="nav_verify"):
            st.session_state.page = "verify"
            st.rerun()

    with cols[3]:
        if st.button(f"👤\n{t('profile')}", use_container_width=True, key="nav_profile"):
            st.session_state.page = "profile"
            st.rerun()

    if is_admin() and len(cols) > 4:
        with cols[4]:
            if st.button(f"⚙️\nAdmin", use_container_width=True, key="nav_admin"):
                st.session_state.page = "admin"
                st.rerun()


def render_topbar():
    """Render top bar with language toggle and logout."""
    col1, col2, col3 = st.columns([2, 4, 2])

    with col1:
        lang = st.session_state.get("language", "es")
        new_lang = "en" if lang == "es" else "es"
        flag = "🇺🇸" if lang == "es" else "🇪🇸"
        if st.button(f"{flag}", key="lang_toggle"):
            st.session_state.language = new_lang
            st.rerun()

    with col2:
        role_badge = ""
        if is_verified():
            role_badge = " ✅"
        elif is_authenticated():
            role_badge = " ⏳"
        st.markdown(
            f"<h3 style='text-align:center; color:#FF6B35; margin:0;'>RunnerMatch{role_badge}</h3>",
            unsafe_allow_html=True,
        )

    with col3:
        if is_authenticated():
            if st.button(f"🚪", key="logout_btn", help=t("logout")):
                logout()
                st.rerun()


# =============================================================================
# MAIN APP
# =============================================================================

def main():
    render_topbar()

    if not is_authenticated():
        from pages.auth_page import render_login
        render_login()
        return

    # Set default page based on user state
    if "page" not in st.session_state:
        if is_admin():
            st.session_state.page = "admin"
        elif is_verified():
            st.session_state.page = "discover"
        else:
            st.session_state.page = "profile"

    page = st.session_state.get("page", "discover")

    # Render current page
    if page == "discover":
        from pages.discover_page import render_discover
        render_discover()
    elif page == "messages":
        from pages.messages_page import render_messages
        render_messages()
    elif page == "verify":
        from pages.verify_page import render_verify
        render_verify()
    elif page == "profile":
        from pages.profile_page import render_profile
        render_profile()
    elif page == "admin":
        from pages.admin_page import render_admin
        render_admin()
    else:
        st.session_state.page = "discover"
        st.rerun()

    # Bottom navigation
    render_navigation()


if __name__ == "__main__":
    main()
