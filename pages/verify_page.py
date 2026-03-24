"""
RunnerMatch - Race Verification Page
Users verify their race enrollment to unlock matching.
"""

import streamlit as st
from i18n import t
import auth
from database import get_db, Race, RaceVerification
from verification import verify_runner, get_user_verifications


def render_verify():
    """Render race verification page."""
    auth.require_auth()
    user_id = st.session_state.user_db_id

    st.markdown(f"### {t('verify_race')}")

    db = next(get_db())
    try:
        # Show existing verifications
        existing = get_user_verifications(db, user_id)
        if existing:
            for v in existing:
                status_icon = {"verified": "✅", "pending": "⏳", "rejected": "❌"}.get(v["status"], "❓")
                st.markdown(
                    f"{status_icon} **{v['race_name']}** ({v['race_country']}) — "
                    f"{t(f'verification_{v[\"status\"]}') if v['status'] != 'verified' else t('verification_success')}"
                )

            if any(v["status"] == "verified" for v in existing):
                st.success(t("verification_success"))
                st.markdown("---")

        # Get available races
        races = db.query(Race).filter_by(is_active=True).order_by(Race.date.desc()).all()

        if not races:
            st.warning(
                "No hay carreras disponibles aún. El administrador debe agregar carreras. / "
                "No races available yet. Admin needs to add races."
            )
            return

        # Race selection
        race_options = {r.id: f"{r.name} - {r.city}, {r.country} ({r.year})" for r in races}

        selected_race_id = st.selectbox(
            t("select_race"),
            options=list(race_options.keys()),
            format_func=lambda x: race_options[x],
        )

        # Check if already verified for this race
        already = db.query(RaceVerification).filter_by(
            user_id=user_id, race_id=selected_race_id, status="verified"
        ).first()

        if already:
            st.info(t("already_verified"))
            return

        # Verification form
        with st.form("verify_form"):
            st.markdown(f"**{t('your_full_name')}**")
            submitted_name = st.text_input(
                t("your_full_name"),
                placeholder="Juan Carlos Pérez López",
                label_visibility="collapsed",
            )

            submitted_bib = st.text_input(
                t("bib_number"),
                placeholder="123",
                help="Opcional pero ayuda a verificar más rápido / Optional but helps verify faster",
            )

            submit = st.form_submit_button(t("verify_button"), use_container_width=True)

        if submit:
            if not submitted_name:
                st.error(t("required_field"))
                return

            with st.spinner(t("loading")):
                result = verify_runner(
                    db=db,
                    user_id=user_id,
                    race_id=selected_race_id,
                    submitted_name=submitted_name,
                    submitted_bib=submitted_bib,
                )

            if result["status"] == "verified":
                st.balloons()
                st.success(t("verification_success"))
                if result["matched_name"]:
                    st.info(
                        f"Matched: **{result['matched_name']}** "
                        f"(score: {result['score']}%)"
                    )
                st.session_state.user_role = "verified"
                st.rerun()

            elif result["status"] == "pending":
                st.warning(t("verification_pending"))
                st.info(
                    f"Closest match: **{result['matched_name']}** "
                    f"(score: {result['score']}%)"
                )

            elif result["status"] == "no_participants":
                st.warning(
                    "No hay lista de participantes para esta carrera aún. / "
                    "No participant list available for this race yet."
                )

            elif result["status"] == "already_verified":
                st.info(t("already_verified"))

            else:
                st.error(t("verification_failed"))
                if result["matched_name"]:
                    st.info(
                        f"Best match found: **{result['matched_name']}** "
                        f"(score: {result['score']}%) — "
                        f"{'Muy bajo para auto-verificar' if st.session_state.language == 'es' else 'Too low to auto-verify'}"
                    )

    finally:
        db.close()
