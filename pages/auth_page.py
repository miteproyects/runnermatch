"""
RunnerMatch - Authentication Pages (Login, Signup, Reset Password)
"""

import streamlit as st
from i18n import t, language_selector
import auth
from database import get_db, User, Profile


def render_login():
    """Render login page."""
    st.markdown(
        """
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #FF6B35; font-size: 2.5em;">RunnerMatch</h1>
            <p style="color: #666; font-size: 1.1em;">Conecta con corredores verificados / Connect with verified runners</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    language_selector()
    st.markdown("---")

    tab_login, tab_signup = st.tabs([t("login"), t("signup")])

    with tab_login:
        _render_login_form()

    with tab_signup:
        _render_signup_form()


def _render_login_form():
    """Login form."""
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(t("email"), placeholder="corredor@email.com")
        password = st.text_input(t("password"), type="password")
        submitted = st.form_submit_button(t("login"), use_container_width=True)

    if submitted:
        if not email or not password:
            st.error(t("required_field"))
            return

        with st.spinner(t("loading")):
            result = auth.sign_in(email, password)

        if result["success"]:
            # Get or create user in database
            db = next(get_db())
            try:
                user = db.query(User).filter_by(firebase_uid=result["uid"]).first()
                if user:
                    auth.set_authenticated(
                        uid=result["uid"],
                        email=result["email"],
                        id_token=result["id_token"],
                        refresh_token=result["refresh_token"],
                        role=user.role,
                        db_id=user.id,
                    )
                    st.session_state.language = user.language
                else:
                    # User exists in Firebase but not in our DB (edge case)
                    new_user = User(
                        firebase_uid=result["uid"],
                        email=result["email"],
                        language=st.session_state.get("language", "es"),
                    )
                    db.add(new_user)
                    db.commit()
                    auth.set_authenticated(
                        uid=result["uid"],
                        email=result["email"],
                        id_token=result["id_token"],
                        refresh_token=result["refresh_token"],
                        role="unverified",
                        db_id=new_user.id,
                    )
            finally:
                db.close()

            st.rerun()
        else:
            error_key = result.get("error", "error")
            if error_key in ("invalid_credentials", "email_exists", "weak_password",
                             "user_disabled", "too_many_attempts"):
                st.error(t(error_key))
            else:
                st.error(f"{t('error')}: {error_key}")

    # Forgot password link
    if st.button(t("forgot_password"), type="secondary"):
        st.session_state.show_reset = True
        st.rerun()

    if st.session_state.get("show_reset"):
        _render_reset_form()


def _render_signup_form():
    """Signup form."""
    with st.form("signup_form", clear_on_submit=False):
        email = st.text_input(t("email"), placeholder="corredor@email.com", key="signup_email")
        password = st.text_input(t("password"), type="password", key="signup_pass")
        confirm = st.text_input(t("confirm_password"), type="password", key="signup_confirm")
        submitted = st.form_submit_button(t("signup"), use_container_width=True)

    if submitted:
        if not email or not password:
            st.error(t("required_field"))
            return
        if password != confirm:
            st.error(t("password_mismatch"))
            return
        if len(password) < 6:
            st.error(t("weak_password"))
            return

        with st.spinner(t("loading")):
            result = auth.sign_up(email, password)

        if result["success"]:
            # Create user in database
            db = next(get_db())
            try:
                new_user = User(
                    firebase_uid=result["uid"],
                    email=email,
                    language=st.session_state.get("language", "es"),
                )
                db.add(new_user)
                db.commit()

                auth.set_authenticated(
                    uid=result["uid"],
                    email=email,
                    id_token=result["id_token"],
                    refresh_token=result["refresh_token"],
                    role="unverified",
                    db_id=new_user.id,
                )
            finally:
                db.close()

            st.success(t("verification_email_sent"))
            st.rerun()
        else:
            error_key = result.get("error", "error")
            if error_key in ("email_exists", "weak_password", "invalid_email"):
                st.error(t(error_key))
            else:
                st.error(f"{t('error')}: {error_key}")


def _render_reset_form():
    """Password reset form."""
    st.markdown(f"### {t('reset_password')}")
    with st.form("reset_form"):
        email = st.text_input(t("email"), key="reset_email")
        submitted = st.form_submit_button(t("submit"))

    if submitted and email:
        result = auth.reset_password(email)
        if result["success"]:
            st.success(t("reset_email_sent"))
            st.session_state.show_reset = False
        else:
            st.error(t("error"))
