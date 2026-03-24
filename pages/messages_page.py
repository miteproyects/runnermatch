"""
RunnerMatch - Messages Page
Chat interface for matched users.
"""

import streamlit as st
from i18n import t
import auth
from database import get_db
from chat import get_conversations_preview, get_messages, send_message
from matching import get_user_matches


def render_messages():
    """Render the messages/chat page."""
    auth.require_verified()
    user_id = st.session_state.user_db_id

    st.markdown(f"### {t('messages')}")

    db = next(get_db())
    try:
        # If a specific chat is active, show it
        if st.session_state.get("active_chat"):
            _render_chat(db, user_id, st.session_state.active_chat)
            return

        # Otherwise show conversations list
        conversations = get_conversations_preview(db, user_id)

        if not conversations:
            # Show matches without messages
            matches = get_user_matches(db, user_id)
            if matches:
                st.markdown(f"**{t('matches')}**")
                for m in matches:
                    cols = st.columns([1, 4, 1])
                    with cols[0]:
                        if m["primary_photo_url"] and not m["primary_photo_url"].startswith("/placeholder"):
                            st.image(m["primary_photo_url"], width=50)
                        else:
                            st.markdown("🏃")
                    with cols[1]:
                        st.markdown(f"**{m['display_name']}**")
                        if m.get("preferred_distance"):
                            st.caption(f"🏃 {m['preferred_distance']}")
                    with cols[2]:
                        if st.button(t("send_message"), key=f"msg_{m['match_id']}"):
                            st.session_state.active_chat = m["match_id"]
                            st.rerun()
                    st.markdown("---")
            else:
                st.markdown(
                    f"""
                    <div style="text-align: center; padding: 60px 20px;">
                        <p style="font-size: 3em;">💬</p>
                        <p style="color: #666;">{t('no_matches')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            return

        # Conversation list
        for conv in conversations:
            cols = st.columns([1, 5, 1])
            with cols[0]:
                if conv["primary_photo_url"] and not conv["primary_photo_url"].startswith("/placeholder"):
                    st.image(conv["primary_photo_url"], width=50)
                else:
                    st.markdown("🏃")
            with cols[1]:
                unread_badge = f" ({conv['unread_count']})" if conv["unread_count"] > 0 else ""
                st.markdown(f"**{conv['display_name']}{unread_badge}**")
                preview = conv["last_message"][:60]
                prefix = "→ " if conv["is_last_mine"] else ""
                st.caption(f"{prefix}{preview}")
            with cols[2]:
                if st.button("💬", key=f"chat_{conv['match_id']}"):
                    st.session_state.active_chat = conv["match_id"]
                    st.rerun()

            st.markdown("---")

    finally:
        db.close()


def _render_chat(db, user_id: int, match_id: int):
    """Render a single chat conversation."""
    # Back button
    if st.button(f"← {t('back')}"):
        del st.session_state.active_chat
        st.rerun()

    # Get messages
    messages = get_messages(db, match_id, user_id, limit=50)

    # Chat container
    chat_container = st.container()

    with chat_container:
        if not messages:
            st.markdown(
                f"<p style='text-align:center; color:#999;'>{t('no_messages')}</p>",
                unsafe_allow_html=True,
            )

        for msg in messages:
            if msg["is_mine"]:
                st.chat_message("user").markdown(msg["content"])
            else:
                st.chat_message("assistant").markdown(msg["content"])

    # Message input
    with st.form("send_msg", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            new_msg = st.text_input(
                t("type_message"),
                placeholder=t("type_message"),
                label_visibility="collapsed",
            )
        with col_btn:
            sent = st.form_submit_button("📩")

    if sent and new_msg:
        result = send_message(db, match_id, user_id, new_msg)
        if result["success"]:
            st.rerun()
        else:
            st.error(t("error"))
