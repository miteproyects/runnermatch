"""
RunnerMatch - Database Module
PostgreSQL connection and table management via SQLAlchemy.
"""

import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, DateTime,
    Text, ForeignKey, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.pool import QueuePool
import config

# =============================================================================
# ENGINE & SESSION
# =============================================================================
engine = create_engine(
    config.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
) if config.DATABASE_URL else None

SessionLocal = sessionmaker(bind=engine) if engine else None
Base = declarative_base()


def get_db():
    """Get a database session. Use with context manager."""
    if not SessionLocal:
        raise RuntimeError("Database not configured. Set DATABASE_URL.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    if engine:
        Base.metadata.create_all(bind=engine)


# =============================================================================
# MODELS
# =============================================================================

class User(Base):
    __tablename_^ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    firebase_uid = Column(String(128), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(20), default="unverified")  # unverified, verified, admin
    language = Column(String(5), default="es")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    verifications = relationship("RaceVerification", back_populates="user", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="user", cascade="all, delete-orphan")
    sent_likes = relationship("Like", foreign_keys="Like.from_user_id", back_populates="from_user")
    received_likes = relationship("Like", foreign_keys="Like.to_user_id", back_populates="to_user")
    matches_as_user1 = relationship("Match", foreign_keys="Match.user1_id", back_populates="user1")
    matches_as_user2 = relationship("Match", foreign_keys="Match.user2_id", back_populates="user2")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    display_name = Column(String(100))
    bio = Column(Text, default="")
    gender = Column(String(20))
    looking_for = Column(String(20))  # male, female, both
    birth_date = Column(DateTime)
    city = Column(String(100))
    country = Column(String(100))

    # Runner-specific mandatory fields
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    bmi = Column(Float)

    # Running stats
    preferred_distance = Column(String(50))  # 5K, 10K, 21K, 42K, trail, ultra
    avg_pace_min_km = Column(Float)  # minutes per km
    years_running = Column(Integer)
    weekly_km = Column(Float)

    profile_complete = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="profile")

    def calculate_bmi(self):
        if self.height_cm and self.weight_kg and self.height_cm > 0:
            height_m = self.height_cm / 100
            self.bmi = round(self.weight_kg / (height_m ** 2), 1)


class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    country = Column(String(100), nullable=False)
    city = Column(String(100))
    date = Column(DateTime)
    year = Column(Integer)
    distance_categories = Column(Text)  # JSON string: ["5K","10K","50K"]
    source_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    participants = relationship("RaceParticipant", back_populates="race", cascade="all, delete-orphan")
    verifications = relationship("RaceVerification", back_populates="race")


class RaceParticipant(Base):
    __tablename__ = "race_participants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(255), nullable=False)
    full_name_normalized = Column(String(255), nullable=False, index=True)
    bib_number = Column(String(20))
    category = Column(String(50))
    finish_time = Column(String(20))
    nationality = Column(String(100))
    source = Column(String(50))  # scraped, manual_upload, api

    race = relationship("Race", back_populates="participants")

    __table_args__ = (
        Index("ix_participant_race_name", "race_id", "full_name_normalized"),
    )


class RaceVerification(Base):
    __tablename__ = "race_verifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    race_id = Column(Integer, ForeignKey("races.id", ondelete="SET NULL"))
    submitted_name = Column(String(255), nullable=False)
    submitted_bib = Column(String(20))
    matched_participant_id = Column(Integer, ForeignKey("race_participants.id"))
    match_score = Column(Integer)  # fuzzy match score 0-100
    status = Column(String(20), default="pending")  # pending, verified, rejected
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="verifications")
    race = relationship("Race", back_populates="verifications")

    __table_args__ = (
        UniqueConstraint("user_id", "race_id", name="uq_user_race_verification"),
    )


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(500), nullable=False)
    storage_path = Column(String(500))
    is_primary = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="photos")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_like = Column(Boolean, nullable=False)  # True = like, False = pass
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="sent_likes")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="received_likes")

    __table_args__ = (
        UniqueConstraint("from_user_id", "to_user_id", name="uq_like_pair"),
    )


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user1_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    matched_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    user1 = relationship("User", foreign_keys=[user1_id], back_populates="matches_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="matches_as_user2")

    __table_args__ = (
        UniqueConstraint("user1_id", "user2_id", name="uq_match_pair"),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)

    match = relationship("Match")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False)
    details = Column(Text)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
