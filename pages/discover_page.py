"""
RunnerMatch - Discover Page (Swipe/Like Interface)
Tinder/Bumble-style card swiping for verified runners.
"""

import streamlit as st
from i18n import t
import auth
from database import get_db, User, Profile
from matching import get_discovery_feed, record_swipe


def render_discover():
    """Render the discovery/swipe page."""
    auth.require_verified()
    user_id = st.session_state.user_db_id

    st.markdown(f"### {t('discover')}")

    # Check if profile is complete
    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user or not user.profile or not user.profile.profile_complete:
            st.warning(t("profile_incomplete"))
            if st.button(t("edit_profile")):
                st.session_state.page = "profile"
                st.rerun()
            return

        # Load feed if not cached or exhausted
        if "discovery_feed" not in st.session_state or not st.session_state.discovery_feed:
            feed = get_discovery_feed(db, user_id, limit=20)
            st.session_state.discovery_feed = feed
            st.session_state.discovery_index = 0

        feed = st.session_state.discovery_feed
        idx = st.session_state.get("discovery_index", 0)

        if idx >= len(feed):
            st.markdown(
                f"""
                <div style="text-align: center; padding: 60px 20px;">
                    <p style="font-size: 3em;">🏃</p>
                    <p style="font-size: 1.2em; color: #666;">{t('no_more_profiles')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("🔄 Refresh / Actualizar"):
                st.session_state.discovery_feed = []
                st.session_state.discovery_index = 0
                st.rerun()
            return

        # Display current profile card
        profile = feed[idx]
        _render_profile_card(profile)

        # Action buttons
        col_pass, col_spacer, col_like = st.columns([2, 1, 2])

        with col_pass:
            if st.button(f"👋 {t('pass')}", use_container_width=True, key="btn_pass"):
                result = record_swipe(db, user_id, profile["user_id"], is_like=False)
                st.session_state.discovery_index = idx + 1
                st.rerun()

        with col_like:
            if st.button(f"❤️ {t('like')}", use_container_width=True, key="btn_like", type="primary"):
                result = record_swipe(db, user_id, profile["user_id"], is_like=True)
                st.session_state.discovery_index = idx + 1

                if result["matched"]:
                    st.session_state.show_match = {
                        "name": profile["display_name"],
                        "photo": profile["primary_photo_url"],
                        "match_id": result["match_id"],
                    }

                st.rerun()

        # Show match popup
        if st.session_state.get("show_match"):
            _render_match_popup(st.session_state.show_match)
            if st.button(t("send_message"), type="primary"):
                st.session_state.page = "messages"
                st.session_state.active_chat = st.session_state.show_match["match_id"]
                del st.session_state.show_match
                st.rerun()
            if st.button("OK"):
                del st.session_state.show_match
                st.rerun()

    finally:
        db.close()


def _render_profile_card(profile: dict):
    """Render a swipeable profile card."""
    st.markdown(
        f"""
        <div style="background: white; border-radius: 16px; padding: 20px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 400px;
                    margin: 0 auto;">
        """,
        unsafe_allow_html=True,
    )

    # Photo
    if profile["primary_photo_url"] and not profile["primary_photo_url"].startswith("/placeholder"):
        st.image(profile["primary_photo_url"], use_container_width=True)
    else:
        st.markdown(
            """<div style="background: #f0f0f0; height: 300px; border-radius: 12px;
                          display: flex; align-items: center; justify-content: center;
                          font-size: 4em;">🏃</div>""",
            unsafe_allow_html=True,
        )

    # Name and age
    age_str = f", {profile['age']}" if profile["age"] else ""
    st.markdown(f"### {profile['display_name']}{age_str}")

    if profile["city"]:
        st.markdown(f"📍 {profile['city']}, {profile.get('country', '')}")

    # Verified badge
    if profile["verified_races_count"] > 0:
        st.markdown(f"✅ {profile['verified_races_count']} {'carreras verificadas' if st.session_state.language == 'es' else 'verified races'}")

    # Bio
    if profile["bio"]:
        st.markdown(f"_{profile['bio']}_")

    # Runner stats
    st.markdown("---")
    cols = st.columns(4)
    with cols[0]:
        st.metric(t("preferred_distance"), profile["preferred_distance"] or "—")
    with cols[1]:
        pace = f"{profile['avg_pace_min_km']:.1f}" if profile["avg_pace_min_km"] else "—"
        st.metric(t("avg_pace"), f"{pace}")
    with cols[2]:
        st.metric(t("weekly_km"), f"{profile['weekly_km']:.0f}" if profile["weekly_km"] else "—")
    with cols[3]:
        st.metric(t("years_running"), profile["years_running"] or "—")

    # Physical stats
    cols2 = st.columns(3)
    with cols2[0]:
        st.metric(t("height_cm"), f"{profile['height_cm']:.0f}" if profile["height_cm"] else "—")
    with cols2[1]:
        st.metric(t("weight_kg"), f"{profile['weight_kg']:.0f}" if profile["weight_kg"] else "—")
    with cols2[2]:
        bmi = profile.get("bmi")
        st.metric(t("bmi"), f"{bmi:.1f}" if bmi else "—")

    st.markdown("</div>", unsafe_allow_html=True)


def _render_match_popup(match_info: dict):
    """Render the 'It's a Match!' popup."""
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #FF6B35, #FF8C61);
                    border-radius: 16px; padding: 40px 20px; text-align: center;
                    color: white; margin: 20px 0;">
            <h1 style="color: white; font-size: 2em;">🎉 {t('its_a_match')}</h1>
            <p style="font-size: 1.2em;">
                {t('match_message', name=match_info['name'])}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
