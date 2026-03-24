"""
RunnerMatch - Race Verification Engine
Fuzzy-matches user-submitted names against scraped participant lists.
"""

from thefuzy import fuzy, process
from sqlalchemy.orm import Session
from database import RaceParticipant, RaceVerification, User, Race
from scraper import normalize_name
import config
import datetime


def verify_runner(
    db: Session,
    user_id: int,
    race_id: int,
    submitted_name: str,
    submitted_bib: str = "",
) -> dict:
    """
    Attempt to verify a user against a race participant list.

    Strategy:
    1. If bib number provided, try exact bib match first.
    2. Fuzzy match name against all participants in that race.
    3. If score >= threshold, auto-verify. Otherwise, flag for manual review.

    Returns: {"status": "verified"|"pending"|"rejected", "score": int, "matched_name": str}
    """
    # Check if already verified for this race
    existing = db.query(RaceVerification).filter_by(
        user_id=user_id, race_id=race_id
    ).first()
    if existing and existing.status == "verified":
        return {"status": "already_verified", "score": 100, "matched_name": ""}

    # Get all participants for this race
    participants = db.query(RaceParticipant).filter_by(race_id=race_id).all()
    if not participants:
        return {"status": "no_participants", "score": 0, "matched_name": ""}

    normalized_submitted = normalize_name(submitted_name)
    best_match = None
    best_score = 0

    # Strategy 1: Exact bib match
    if submitted_bib:
        for p in participants:
            if p.bib_number and p.bib_number.strip() == submitted_bib.strip():
                # Bib matches, now check name similarity
                name_score = fuzz.token_sort_ratio(
                    normalized_submitted, p.full_name_normalized
                )
                if name_score > best_score:
                    best_score = name_score
                    best_match = p

    # Strategy 2: Fuzzy name match across all participants
    if best_score < config.FUZZY_MATCH_THRESHOLD:
        name_list = [(p.full_name_normalized, p.id) for p in participants]
        names_only = [n[0] for n in name_list]

        # Use token_sort_ratio for best results with name order differences
        matches = process.extract(
            normalized_submitted,
            names_only,
            scorer=fuzz.token_sort_ratio,
            limit=5,
        )

        for match_name, score, idx in matches:
            if score > best_score:
                best_score = score
                # Find the participant object
                for p in participants:
                    if p.full_name_normalized == match_name:
                        best_match = p
                        break

    # Determine verification status
    if best_score >= config.FUZZY_MATCH_THRESHOLD:
        status = "verified"
    elif best_score >= 60:
        status = "pending"  # Close enough for manual review
    else:
        status = "rejected"

    # Save or update verification record
    verification = existing or RaceVerification(user_id=user_id, race_id=race_id)
    verification.submitted_name = submitted_name
    verification.submitted_bib = submitted_bib
    verification.match_score = best_score
    verification.status = status
    verification.matched_participant_id = best_match.id if best_match else None

    if status == "verified":
        verification.verified_at = datetime.datetime.utcnow()
        # Update user role
        user = db.query(User).filter_by(id=user_id).first()
        if user and user.role == "unverified":
            user.role = "verified"

    if not existing:
        db.add(verification)

    db.commit()

    return {
        "status": status,
        "score": best_score,
        "matched_name": best_match.full_name if best_match else "",
    }


def get_user_verifications(db: Session, user_id: int) -> list[dict]:
    """Get all verification records for a user."""
    verifications = (
        db.query(RaceVerification, Race)
        .join(Race, RaceVerification.race_id == Race.id)
        .filter(RaceVerification.user_id == user_id)
        .all()
    )
    return [
        {
            "race_name": race.name,
            "race_country": race.country,
            "status": v.status,
            "score": v.match_score,
            "submitted_name": v.submitted_name,
            "verified_at": v.verified_at,
        }
        for v, race in verifications
    ]


def get_pending_verifications(db: Session) -> list[dict]:
    """Get all pending verifications (for admin review)."""
    pending = (
        db.query(RaceVerification, User, Race)
        .join(User, RaceVerification.user_id == User.id)
        .join(Race, RaceVerification.race_id == Race.id)
        .filter(RaceVerification.status == "pending")
        .order_by(RaceVerification.created_at.desc())
        .all()
    )
    return [
        {
            "verification_id": v.id,
            "user_email": user.email,
            "race_name": race.name,
            "submitted_name": v.submitted_name,
            "submitted_bib": v.submitted_bib,
            "match_score": v.match_score,
            "created_at": v.created_at,
        }
        for v, user, race in pending
    ]


def approve_verification(db: Session, verification_id: int):
    """Admin approves a pending verification."""
    v = db.query(RaceVerification).filter_by(id=verification_id).first()
    if v:
        v.status = "verified"
        v.verified_at = datetime.datetime.utcnow()
        user = db.query(User).filter_by(id=v.user_id).first()
        if user and user.role == "unverified":
            user.role = "verified"
        db.commit()


def reject_verification(db: Session, verification_id: int):
    """Admin rejects a pending verification."""
    v = db.query(RaceVerification).filter_by(id=verification_id).first()
    if v:
        v.status = "rejected"
        db.commit()
