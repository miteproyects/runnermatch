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
                    <p style="font-size: 3em;">ğŸƒ</p>
                    <p style="font-size: 1.2em; color: #666;">{t('no_more_profiles')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("ğŸ”„ Refresh / Actualizar"):
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
            if st.button(f"ğŸ‘‹ {t('pass')}", use_container_width=True, key="btn_pass"):
                result = record_swipe(db, user_id, profile["user_id"], is_like=False)
                st.session_state.discovery_index = idx + 1
                st.rerun()

        with col_like:
            if st.button(f"â¤ï¸ {t('like')}", use_container_width=True, key="btn_like", type="primary"):
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
        st.markdown*        """<div style="background: #f0f0f0; height: 300px; border-radius: 12px;
                          display: flex; align-items: center; justify-content: center;
                          font-size: 4em;">ğŸƒ</div>""",
            unsafe_allow_html=True,
        )

    # Name and age
    age_str = f", {profile['age']}" if profile["age"] else ""
    st.markdown(f"### {profile['display_name']}{age_str}")

    if profile["city"]:
        st.markdown(f"ğŸ“ {profile['city']}, {profile.get('country', '')}")

    # Verified badge
    if profile["verified_races_count"] > 0:
        st.markdown(f"â¤ï¸ {profile['verified_races_count']} {'carreras verificadas' if st.session_state.language == 'es' else 'verified races'}")

    # Bio
    if profile["bio"]:
        st.markdown(f"_{profile['bio']}_")

    # Runner stats
    st.markdown("---")
    cols = st.columns(4)
    with cols[0]:
        st.metric(t("preferred_distance"), profile["preferred_distance"] or bâ€”")
    with cols[1]:
        pace = f"{profile['avg_pace_min_km']:.1f}" if profile["avg_pace_min_km"] else "â€”"
        st.metric(t("avg_pace"), f"{p{
•õôˆ¤(€€€İ¥Ñ ½±ÍlÉtè(€€€€€€€ÍĞ¹µ•ÑÉ¥Œ¡Ğ ‰İ••­±å}­´ˆ¤°˜‰íÁÉ½™¥±•lİ••­±å}­´tè¸Á™ôˆ¥˜ÁÉ½™¥±•l‰İ••­±å}­´‰t•±Í”€‹ŠPˆ¤(€€€İ¥Ñ ½±ÍlÍtè(€€€€€€€ÍĞ¹µ•ÑÉ¥Œ¡Ğ ‰å•…ÉÍ}ÉÕ¹¹¥¹œˆ¤°ÁÉ½™¥±•l‰å•…ÉÍ}ÉÕ¹¹¥¹œ‰t½ÈƒŠPˆ¤(((€€€€ŒA¡åÍ¥…°ÍÑ…ÑÌ(€€€½±ÌÈ€ôÍĞ¹½±Õµ¹Ì Ì¤(€€€İ¥Ñ ½±ÌÉlÁtè(€€€€€€€ÍĞ¹µ•ÑÉ¥Œ¡Ğ ‰¡•¥¡Ñ}´ˆ¤°˜‰íÁÉ½™¥±•l¡•¥¡Ñ}´tè¸Á™ôˆ¥˜ÁÉ½™¥±•l‰¡•¥¡Ñ}´‰t•±Í”€‹ŠPˆ¤(€€€İ¥Ñ ½±ÌÉlÅtè(€€€€€€€ÍĞ¹µ•ÑÉ¥Œ¡Ğ ‰İ•¥¡Ñ}­œˆ¤°˜‰íÁÉ½™¥±•lİ•¥¡Ñ}­œtè¸Á™ôˆ¥˜ÁÉ½™¥±•l‰İ•¥¡Ñ}­œ‰t•±Í”€‹ŠPˆ¤(€€€İ¥Ñ ½±ÍˆÉlÉtè(€€€€€€€‰µ¤€ôÁÉ½™¥±”¹•Ğ ‰‰µ¤ˆ¤(€€€€€€€ÍĞ¹µ•ÑÉ¥Œ¡Ğ ‰‰µ¤ˆ¤°˜‰í‰µ¤è¸Å™ôˆ¥˜‰µ¤•±Í”ƒŠPˆ¤((€€€ÍĞ¹µ…É­‘½İ¸ ˆğ½‘¥Øøˆ°Õ¹Í…™•}…±±½İ}¡Ñµ°õQÉÕ”¤(()‘•˜}É•¹‘•É}µ…Ñ¡}Á½ÁÕÀ¡µ…Ñ¡}¥¹™¼è‘¥Ğ¤è(€€€€ˆˆ‰I•¹‘•ÈÑ¡”€%ĞÌ„5…Ñ „œÁ½ÁÕÀ¸ˆˆˆ(€€€ÍĞ¹µ…É­‘½İ¸ (€€€€€€€˜ˆˆˆ(€€€€€€€€ñ‘¥ØÍÑå±”ô‰‰…­É½Õ¹è±¥¹•…ÈµÉ…‘¥•¹Ğ ÄÌÕ‘•œ°€ÙÌÔ°€áØÄ¤ì(€€€€€€€€€€€€€€€€€€€‰½É‘•ÈµÉ…‘¥ÕÌè€ÄÙÁàìÁ…‘‘¥¹œè€ĞÁÁà€ÈÁÁàìÑ•áĞµ…±¥¸è•¹Ñ•Èì(€€€€€€€€€€€€€€€€€€€½±½Èèİ¡¥Ñ”ìµ…É¥¸è€ÈÁÁà€Àìˆø(€€€€€€€€€€€€ñ ÄÍÑå±”ô‰½±½Èèİ¡¥Ñ”ì™½¹ĞµÍ¥é”è€É•´ìˆûÂ~:$íĞ ¥ÑÍ}…}µ…Ñ œ¥ôğ½ Äø(€€€€€€€€€€€€ñÀÍÑå±”ô‰™½¹ĞµÍ¥é”è€Ä¸É•´ìˆø(€€€€€€€€€€€€€€€íĞ µ…Ñ¡}µ•ÍÍ…”œ°¹…µ”õµ…Ñ¡}¥¹™½l¹…µ”t¥ô(€€€€€€€€€€€€ğ½Àø(€€€€€€€€ğ½‘¥Øø(€€€€€€€€ˆˆˆ°(€€€€€€€Õ¹Í…™•}…±±½İ}¡Ñµ°õQÉÕ”°(€€€€¤(