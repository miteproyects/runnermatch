"""
RunnerMatch - Profile Page
Create and edit user profile with mandatory height/weight.
"""

import datetime
import streamlit as st
from i18n import t
import auth
from database import get_db, User, Profile, Photo


def render_profile():
    """Render profile creation/edit page."""
    auth.require_auth()

    st.markdown(f"### {t('profile')}")
    user_id = st.session_state.user_db_id

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        profile = user.profile if user else None

        # If profile exists, pre-populate
        defaults = {
            "first_name": profile.first_name if profile else "",
            "last_name": profile.last_name if profile else "",
            "display_name": profile.display_name if profile else "",
            "bio": profile.bio if profile else "",
            "gender": profile.gender if profile else "",
            "looking_for": profile.looking_for if profile else "",
            "birth_date": profile.birth_date.date() if profile and profile.birth_date else datetime.date(1990, 1, 1),
            "city": profile.city if profile else "",
            "country": profile.country if profile else "Ecuador",
            "height_cm": profile.height_cm if profile else 170.0,
            "weight_kg": profile.weight_kg if profile else 70.0,
            "preferred_distance": profile.preferred_distance if profile else "",
            "avg_pace": profile.avg_pace_min_km if profile else 5.5,
            "years_running": profile.years_running if profile else 1,
            "weekly_km": profile.weekly_km if profile else 20.0,
        }

        with st.form("profile_form"):
            st.markdown(f"**{t('first_name')} / {t('last_name')}**")
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input(t("first_name"), value=defaults["first_name"])
            with col2:
                last_name = st.text_input(t("last_name"), value=defaults["last_name"])

            display_name = st.text_input(
                t("display_name"),
                value=defaults["display_name"],
                help="Nombre que otros verán / Name others will see",
            )

            bio = st.text_area(t("bio"), value=defaults["bio"], max_chars=500, height=100)

            col3, col4 = st.columns(2)
            with col3:
                gender_options = ["", "male", "female", "other"]
                gender_labels = ["--", t("gender_male"), t("gender_female"), t("gender_other")]
                gender_idx = gender_options.index(defaults["gender"]) if defaults["gender"] in gender_options else 0
                gender = st.selectbox(t("gender"), options=gender_options,
                                      format_func=lambda x: gender_labels[gender_options.index(x)],
                                      index=gender_idx)

            with col4:
                looking_options = ["", "male", "female", "both"]
                looking_labels = ["--", t("looking_male"), t("looking_female"), t("looking_both")]
                looking_idx = looking_options.index(defaults["looking_for"]) if defaults["looking_for"] in looking_options else 0
                looking_for = st.selectbox(t("looking_for"), options=looking_options,
                                           format_func=lambda x: looking_labels[looking_options.index(x)],
                                           index=looking_idx)

            birth_date = st.date_input(
                t("birth_date"),
                value=defaults["birth_date"],
                min_value=datetime.date(1940, 1, 1),
                max_value=datetime.date.today() - datetime.timedelta(days=365 * 18),
            )

            col5, col6 = st.columns(2)
            with col5:
                city = st.text_input(t("city"), value=defaults["city"])
            with col6:
                country = st.text_input(t("country"), value=defaults["country"])

            # Mandatory runner fields
            st.markdown("---")
            st.markdown(f"**{t('running_stats')}** ({'obligatorio / mandatory' if not profile else ''})")

            col7, col8 = st.columns(2)
            with col7:
                height_cm = st.number_input(
                    t("height_cm"), min_value=100.0, max_value=250.0,
                    value=defaults["height_cm"], step=0.5,
                )
            with col8:
                weight_kg = st.number_input(
                    t("weight_kg"), min_value=30.0, max_value=200.0,
                    value=defaults["weight_kg"], step=0.5,
                )

            # Show BMI calculation live
            if height_cm > 0:
                bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)
                bmi_color = "#4CAF50" if 18.5 <= bmi <= 25 else "#FF9800" if 25 < bmi <= 30 else "#F44336"
                st.markdown(
                    f"{t('bmi')}: <span style='color:{bmi_color}; font-weight:bold;'>{bmi}</span>",
                    unsafe_allow_html=True,
                )

            dist_options = ["5K", "10K", "21K", "42K", "Trail", "Ultra"]
            dist_idx = dist_options.index(defaults["preferred_distance"]) if defaults["preferred_distance"] in dist_options else 0
            preferred_distance = st.selectbox(t("preferred_distance"), options=dist_options, index=dist_idx)

            col9, col10, col11 = st.columns(3)
            with col9:
                avg_pace = st.number_input(
                    t("avg_pace"), min_value=2.0, max_value=15.0,
                    value=defaults["avg_pace"], step=0.1,
                )
            with col10:
                years_running = st.number_input(
                    t("years_running"), min_value=0, max_value=50,
                    value=defaults["years_running"], step=1,
                )
            with col11:
                weekly_km = st.number_input(
                    t("weekly_km"), min_value=0.0, max_value=300.0,
                    value=defaults["weekly_km"], step=5.0,
                )

            submitted = st.form_submit_button(t("save"), use_container_width=True)

        if submitted:
            if not first_name or not last_name:
                st.error(t("required_field"))
                return
            if not gender or not looking_for:
                st.error(t("required_field"))
                return

            _save_profile(
                db, user, profile,
                first_name=first_name,
                last_name=last_name,
                display_name=display_name or first_name,
                bio=bio,
                gender=gender,
                looking_for=looking_for,
                birth_date=datetime.datetime.combine(birth_date, datetime.time()),
                city=city,
                country=country,
                height_cm=height_cm,
                weight_kg=weight_kg,
                preferred_distance=preferred_distance,
                avg_pace_min_km=avg_pace,
                years_running=years_running,
                weekly_km=weekly_km,
            )
            st.success(t("success"))
            st.rerun()

        # Photo upload section
        st.markdown("---")
        _render_photo_upload(db, user_id)

    finally:
        db.close()


def _save_profile(db, user, profile, **fields):
    """Save or update profile."""
    if not profile:
        profile = Profile(user_id=user.id)
        db.add(profile)

    for key, value in fields.items():
        setattr(profile, key, value)

    profile.calculate_bmi()

    # Check if profile is complete
    required = ["first_name", "last_name", "gender", "looking_for", "height_cm", "weight_kg"]
    profile.profile_complete = all(getattr(profile, f) for f in required)

    db.commit()


def _render_photo_upload(db, user_id):
    """Photo upload section."""
    st.markdown(f"**{t('photos')}**")

    existing_photos = (
        db.query(Photo).filter_by(user_id=user_id).order_by(Photo.order_index).all()
    )

    if existing_photos:
        cols = st.columns(min(len(existing_photos), 3))
        for i, photo in enumerate(existing_photos):
            with cols[i % 3]:
                st.image(photo.url, width=150)
                if photo.is_primary:
                    st.caption(f"★ {t('primary_photo')}")

    uploaded = st.file_uploader(
        t("upload_photo"),
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="photo_upload",
    )

    if uploaded:
        st.info(
            "Las fotos se guardarán en Firebase Storage al configurar las credenciales. / "
            "Photos will be saved to Firebase Storage once credentials are configured."
        )
        # In production, upload to Firebase Storage and save URL to DB
        # For MVP/demo, we store as placeholder
        for i, file in enumerate(uploaded):
            if len(existing_photos) + i < 6:  # Max 6 photos
                # Placeholder: in production use firebase_admin.storage
                photo = Photo(
                    user_id=user_id,
                    url=f"/placeholder/{file.name}",
                    is_primary=(len(existing_photos) == 0 and i == 0),
                    order_index=len(existing_photos) + i,
                )
                db.add(photo)

        db.commit()
        st.success(t("success"))
