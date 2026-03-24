"""
RunnerMatch - Admin Panel
Race management, participant uploads, scraping, and user verification review.
"""

import datetime
import streamlit as st
import pandas as pd
from i18n import t
import auth
from database import get_db, Race, RaceParticipant, User, Profile, Match
from scraper import scrape_race, parse_participant_file, normalize_name
from verification import get_pending_verifications, approve_verification, reject_verification


def render_admin():
    """Render admin panel."""
    auth.require_auth()
    if not auth.is_admin():
        st.error("Access denied / Acceso denegado")
        return

    st.markdown(f"### {t('admin_panel')}")

    tab_races, tab_verify, tab_users, tab_stats = st.tabs([
        t("manage_races"),
        t("pending_verifications"),
        t("user_management"),
        "📊 Stats",
    ])

    db = next(get_db())
    try:
        with tab_races:
            _render_race_management(db)

        with tab_verify:
            _render_verification_review(db)

        with tab_users:
            _render_user_management(db)

        with tab_stats:
            _render_stats(db)
    finally:
        db.close()


def _render_race_management(db):
    """Race CRUD and participant management."""

    # Add new race
    st.markdown(f"**{t('add_race')}**")
    with st.form("add_race_form"):
        col1, col2 = st.columns(2)
        with col1:
            race_name = st.text_input(t("race_name"), placeholder="Petzl Trail Plus")
            race_city = st.text_input(t("city"), placeholder="Baños")
            race_country = st.text_input(t("country"), placeholder="Ecuador")
        with col2:
            race_date = st.date_input(t("race_date"), value=datetime.date.today())
            race_year = st.number_input("Year", value=datetime.date.today().year, min_value=2020, max_value=2030)
            categories = st.text_input("Categories (comma separated)", placeholder="5K, 10K, 21K, 50K, 70K")

        source_url = st.text_input("Source URL", placeholder="https://sportmaniacs.com/...")
        add_submitted = st.form_submit_button(t("add_race"), use_container_width=True)

    if add_submitted and race_name:
        slug = race_name.lower().replace(" ", "-") + f"-{race_year}"
        existing = db.query(Race).filter_by(slug=slug).first()
        if existing:
            st.error("This race already exists / Esta carrera ya existe")
        else:
            race = Race(
                name=race_name,
                slug=slug,
                country=race_country,
                city=race_city,
                date=datetime.datetime.combine(race_date, datetime.time()),
                year=race_year,
                distance_categories=categories,
                source_url=source_url,
            )
            db.add(race)
            db.commit()
            st.success(f"Race added: {race_name}")
            st.rerun()

    # List existing races
    st.markdown("---")
    races = db.query(Race).order_by(Race.date.desc()).all()

    for race in races:
        participant_count = db.query(RaceParticipant).filter_by(race_id=race.id).count()

        with st.expander(f"🏁 {race.name} — {race.city}, {race.country} ({race.year}) | {participant_count} participants"):

            # Scrape button
            col_scrape, col_upload = st.columns(2)
            with col_scrape:
                if st.button(f"🔍 {t('scrape_results')}", key=f"scrape_{race.id}"):
                    if race.source_url:
                        with st.spinner("Scraping..."):
                            participants = scrape_race(race.source_url)
                        if participants:
                            _save_participants(db, race.id, participants)
                            st.success(f"Scraped {len(participants)} participants")
                            st.rerun()
                        else:
                            st.warning("No participants found. Try uploading manually.")
                    else:
                        st.warning("No source URL set for this race.")

            # File upload
            with col_upload:
                uploaded = st.file_uploader(
                    t("upload_participants"),
                    type=["csv", "xlsx", "xls"],
                    key=f"upload_{race.id}",
                )
                if uploaded:
                    file_type = "csv" if uploaded.name.endswith(".csv") else "excel"
                    participants = parse_participant_file(uploaded.read(), file_type)
                    if participants:
                        _save_participants(db, race.id, participants)
                        st.success(f"Uploaded {len(participants)} participants")
                        st.rerun()
                    else:
                        st.error("Could not parse file. Check column names.")

            # Show participants preview
            if participant_count > 0:
                participants = (
                    db.query(RaceParticipant)
                    .filter_by(race_id=race.id)
                    .limit(20)
                    .all()
                )
                df = pd.DataFrame([
                    {
                        "Name": p.full_name,
                        "Bib": p.bib_number,
                        "Category": p.category,
                        "Time": p.finish_time,
                        "Source": p.source,
                    }
                    for p in participants
                ])
                st.dataframe(df, use_container_width=True)
                if participant_count > 20:
                    st.caption(f"Showing 20 of {participant_count}")


def _save_participants(db, race_id: int, participants: list[dict]):
    """Save scraped/uploaded participants to DB, avoiding duplicates."""
    existing_names = set(
        p.full_name_normalized
        for p in db.query(RaceParticipant.full_name_normalized).filter_by(race_id=race_id).all()
    )

    added = 0
    for p in participants:
        if p["full_name_normalized"] not in existing_names:
            db.add(RaceParticipant(
                race_id=race_id,
                full_name=p["full_name"],
                full_name_normalized=p["full_name_normalized"],
                bib_number=p.get("bib_number", ""),
                category=p.get("category", ""),
                finish_time=p.get("finish_time", ""),
                nationality=p.get("nationality", ""),
                source=p.get("source", "unknown"),
            ))
            existing_names.add(p["full_name_normalized"])
            added += 1

    db.commit()
    return added


def _render_verification_review(db):
    """Review and approve/reject pending verifications."""
    pending = get_pending_verifications(db)

    if not pending:
        st.info("No pending verifications / No hay verificaciones pendientes")
        return

    st.markdown(f"**{len(pending)} pending**")

    for v in pending:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                st.markdown(f"**{v['submitted_name']}**")
                st.caption(f"Email: {v['user_email']}")
            with col2:
                st.markdown(f"Race: {v['race_name']}")
                st.caption(f"Bib: {v['submitted_bib'] or 'N/A'}")
            with col3:
                score_color = "green" if v["match_score"] >= 70 else "orange"
                st.markdown(f"Score: :{score_color}[**{v['match_score']}%**]")
            with col4:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅", key=f"approve_{v['verification_id']}"):
                        approve_verification(db, v["verification_id"])
                        st.rerun()
                with c2:
                    if st.button("❌", key=f"reject_{v['verification_id']}"):
                        reject_verification(db, v["verification_id"])
                        st.rerun()
            st.markdown("---")


def _render_user_management(db):
    """View and manage users."""
    users = db.query(User).order_by(User.created_at.desc()).all()

    df = pd.DataFrame([
        {
            "ID": u.id,
            "Email": u.email,
            "Role": u.role,
            "Active": u.is_active,
            "Joined": u.created_at.strftime("%Y-%m-%d") if u.created_at else "",
            "Last Active": u.last_active.strftime("%Y-%m-%d") if u.last_active else "",
        }
        for u in users
    ])

    if not df.empty:
        st.dataframe(df, use_container_width=True)

        # Quick admin promotion
        st.markdown("**Promote user to admin**")
        with st.form("promote_form"):
            email = st.text_input("User email")
            if st.form_submit_button("Make Admin"):
                user = db.query(User).filter_by(email=email).first()
                if user:
                    user.role = "admin"
                    db.commit()
                    st.success(f"{email} is now admin")
                    st.rerun()
                else:
                    st.error("User not found")
    else:
        st.info("No users yet")


def _render_stats(db):
    """Dashboard stats with Plotly."""
    import plotly.express as px

    total_users = db.query(User).count()
    verified_users = db.query(User).filter(User.role.in_(["verified", "admin"])).count()
    active_matches = db.query(Match).filter_by(is_active=True).count()
    total_races = db.query(Race).count()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(t("total_users"), total_users)
    with col2:
        st.metric(t("verified_users"), verified_users)
    with col3:
        st.metric(t("active_matches"), active_matches)
    with col4:
        st.metric("Races", total_races)

    # User registration over time
    users = db.query(User).order_by(User.created_at).all()
    if users:
        dates = [u.created_at.date() for u in users if u.created_at]
        if dates:
            df_dates = pd.DataFrame({"date": dates})
            df_dates["count"] = 1
            df_grouped = df_dates.groupby("date").sum().cumsum().reset_index()
            fig = px.line(
                df_grouped, x="date", y="count",
                title="User Growth / Crecimiento de Usuarios",
                labels={"date": "Date", "count": "Users"},
            )
            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
            )
            st.plotly_chart(fig, use_container_width=True)
