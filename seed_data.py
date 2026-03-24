"""
RunnerMatch - Seed Data Script
Populates initial data: Petzl Trail Plus race, sample participants, and admin user.
Run once after database setup: python seed_data.py
"""

import datetime
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from database import engine, SessionLocal, Base, init_db
from database import User, Profile, Race, RaceParticipant
from scraper import normalize_name


def seed():
    """Seed the database with initial data."""
    if not engine:
        print("ERROR: DATABASE_URL not set. Configure it first.")
        return

    # Create tables
    init_db()
    print("✅ Tables created.")

    db = SessionLocal()

    try:
        # =================================================================
        # SEED RACE: Petzl Trail Plus 2026
        # =================================================================
        existing_race = db.query(Race).filter_by(slug="petzl-trail-plus-2026").first()
        if not existing_race:
            petzl = Race(
                name="Petzl Trail Plus",
                slug="petzl-trail-plus-2026",
                country="Ecuador",
                city="Baños de Agua Santa",
                date=datetime.datetime(2026, 4, 9),
                year=2026,
                distance_categories="KV Jr, Km V, 5K, 10K, 20K, 50K, 70K",
                source_url="https://sportmaniacs.com/en/races/petzl-trail-plus-2023-7ma-edicion",
                is_active=True,
            )
            db.add(petzl)
            db.flush()
            race_id = petzl.id
            print(f"✅ Race created: Petzl Trail Plus 2026 (ID: {race_id})")

            # Add sample participants (for testing verification)
            sample_participants = [
                {"full_name": "Juan Carlos Pérez López", "bib_number": "101", "category": "50K"},
                {"full_name": "María Elena Gutiérrez", "bib_number": "102", "category": "21K"},
                {"full_name": "Carlos Andrés Morales", "bib_number": "103", "category": "10K"},
                {"full_name": "Adc:"Ana Lucía Fernández", "bib_number": "104", "category": "50K"},
                {"full_name": "Diego Fernando Castillo", "bib_number": "105", "category": "70K"},
                {"full_name": "Paola Andrea Ramírez", "bib_number": "106", "category": "5K"},
                {"full_name": "RGIi ?d/[to Miguel Sánchez", "bib_number": "107", "category": "21K"},
                {"full_name": "Vae��La>�3&ia Sofía Herrera", "bib_number": "108", "category": "10K"},
                {"full_name": "Andrés Felipe Vargas", "bib_number": "109", "category": "50K"},
                {"full_name": "Camila Alejandra Torres", "bib_number": "110", "category": "70K"},
                {"full_name": "Sebastián Flores", "bib_number": "111", "category": "21K"},
                {"full_name": "Gabutila Paz Mendoza", "bib_number": "112", "category": "10K"},
                {"full_name": "Luis Eduardo Acosta", "bib_number": "113", "category": "50K"},
                {"full_name": "ISD2923��� labella Nicole Paredes", "bib_number": "114", "category": "5K"},
                {"full_name": "Francisco Javier Espinoza", "bib_number": "115", "category": "21K"},
            ]

            for p in sample_participants:
                db.add(RaceParticipant(
                    race_id=race_id,
                    full_name=p["full_name"],
                    full_name_normalized=normalize_name(p["full_name"]),
                    bib_number=p["bib_number"],
                    category=p["category"],
                    source="seed_data",
                ))

            print(f"✅ Added {len(sample_participants)} sample participants.")

        else:
            print("ℹ️  Race already exists, skipping.")

        # =================================================================
        # SEED RACE: Petzl Trail Plus 2025 (historical)
        # =================================================================
        existing_2025 = db.query(Race).filter_by(slug="petzl-trail-plus-2025").first()
        if not existing_2025:
            petzl_2025 = Race(
                name="Petzl Trail Plus",
                slug="petzl-trail-plus-2025",
                country="Ecuador",
                city="Baños de Agua Santa",
                date=datetime.datetime(2025, 4, 10),
                year=2025,
                distance_categories="KV Jr, Km V, 5K, 10K, 20K, 50K, 70K",
                source_url="https://itra.run/Races/RaceDetails/Petzl.Trail.Plus.Trail.de.las.Antenas/2025/101158",
                is_active=True,
            )
            db.add(petzl_2025)
            print("✅ Race created: Petzl Trail Plus 2025 (historical)")

        db.commit()
        print("\n✅ Seed data complete!")
        print("\n📝 Next steps:")
        print("   1. Create an admin user by signing up in the app")
        print("   2. Run: python -c \"from seed_data import promote_admin; promote_admin('your@email.com')\"")
        print("   3. Log in and manage races from the admin panel")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()


def promote_admin(email: str):
    """Promote a user to admin by email."""
    if not engine:
        print("ERROR: DATABASE_URL not set.")
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=email).first()
        if user:
            user.role = "admin"
            db.commit()
            print(f"✅ {email} promoted to admin.")
        else:
            print(f"❌ User not found: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
