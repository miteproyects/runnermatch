"""
RunnerMatch - Matching Engine
Handles discovery feed, likes/passes, and mutual match detection.
"""

import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_, func
from database import User, Profile, Like, Match, Photo, RaceVerification


def get_discovery_feed(db: Session, user_id: int, limit: int = 10) -> list[dict]:
    """
    Get profiles the user hasn't swiped on yet.
    Filters:
    - Only verified users with complete profiles
    - Exclude already liked/passed
    - Exclude already matched
    - Respect gender preferences
    """
    user = db.query(User).filter_by(id=user_id).first()
    if not user or not user.profile:
        return []

    my_profile = user.profile

    # IDs the user already swiped on
    already_swiped = (
        db.query(Like.to_user_id)
        .filter(Like.from_user_id == user_id)
        .subquery()
    )

    # Base query: verified users with complete profiles, not self
    query = (
        db.query(User)
        .join(Profile)
        .filter(
            User.id != user_id,
            User.role.in_(["verified", "admin"]),
            User.is_active == True,
            Profile.profile_complete == True,
            User.id.notin_(already_swiped),
        )
    )

    # Gender preference filter
    if my_profile.looking_for and my_profile.looking_for != "both":
        gender_map = {"male": "male", "female": "female"}
        target_gender = gender_map.get(my_profile.looking_for)
        if target_gender:
            query = query.filter(Profile.gender == target_gender)

    # Also filter: only show users who would be interested in seeing this user
    if my_profile.gender:
        query = query.filter(
            or_(
                Profile.looking_for == "both",
                Profile.looking_for == my_profile.gender,
                Profile.looking_for.is_(None),
            )
        )

    # Order by last active (show most active first)
    candidates = query.order_by(User.last_active.desc()).limit(limit).all()

    results = []
    for candidate in candidates:
        primary_photo = (
            db.query(Photo)
            .filter_by(user_id=candidate.id, is_primary=True)
            .first()
        )
        all_photos = (
            db.query(Photo)
            .filter_by(user_id=candidate.id)
            .order_by(Photo.order_index)
            .all()
        )

        # Get verified races
        verified_races = (
            db.query(RaceVerification)
            .filter_by(user_id=candidate.id, status="verified")
            .all()
        )

        p = candidate.profile
        results.append({
            "user_id": candidate.id,
            "display_name": p.display_name or p.first_name,
            "age": _calculate_age(p.birth_date) if p.birth_date else None,
            "city": p.city,
            "country": p.country,
            "bio": p.bio,
            "height_cm": p.height_cm,
            "weight_kg": p.weight_kg,
            "bmi": p.bmi,
            "preferred_distance": p.preferred_distance,
            "avg_pace_min_km": p.avg_pace_min_km,
            "years_running": p.years_running,
            "weekly_km": p.weekly_km,
            "primary_photo_url": primary_photo.url if primary_photo else None,
            "photo_urls": [ph.url for ph in all_photos],
            "verified_races_count": len(verified_races),
        })

    return results


def record_swipe(db: Session, from_user_id: int, to_user_id: int, is_like: bool) -> dict:
    """
    Record a like or pass. Check for mutual match.
    Returns: {"matched": True/False, "match_id": int or None}
    """
    # Record the swipe
    like = Like(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        is_like=is_like,
    )
    db.add(like)

    result = {"matched": False, "match_id": None}

    if is_like:
        # Check if the other person already liked us
        mutual = (
            db.query(Like)
            .filter_by(from_user_id=to_user_id, to_user_id=from_user_id, is_like=True)
            .first()
        )

        if mutual:
            # It's a match! Create match record (lower ID always user1)
            u1, u2 = sorted([from_user_id, to_user_id])
            existing_match = db.query(Match).filter_by(user1_id=u1, user2_id=u2).first()

            if not existing_match:
                match = Match(user1_id=u1, user2_id=u2)
                db.add(match)
                db.flush()
                result = {"matched": True, "match_id": match.id}

    db.commit()
    return result


def get_user_matches(db: Session, user_id: int) -> list[dict]:
    """Get all active matches for a user with profile info."""
    matches = (
        db.query(Match)
        .filter(
            Match.is_active == True,
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
        )
        .order_by(Match.matched_at.desc())
        .all()
    )

    results = []
    for match in matches:
        other_id = match.user2_id if match.user1_id == user_id else match.user1_id
        other_user = db.query(User).filter_by(id=other_id).first()
        if not other_user or not other_user.profile:
            continue

        primary_photo = (
            db.query(Photo)
            .filter_by(user_id=other_id, is_primary=True)
            .first()
        )

        p = other_user.profile
        results.append({
            "match_id": match.id,
            "user_id": other_id,
            "display_name": p.display_name or p.first_name,
            "age": _calculate_age(p.birth_date) if p.birth_date else None,
            "city": p.city,
            "primary_photo_url": primary_photo.url if primary_photo else None,
            "matched_at": match.matched_at,
            "preferred_distance": p.preferred_distance,
        })

    return results


def unmatch(db: Session, match_id: int, user_id: int):
    """Deactivate a match (unmatch)."""
    match = db.query(Match).filter_by(id=match_id).first()
    if match and (match.user1_id == user_id or match.user2_id == user_id):
        match.is_active = False
        db.commit()


def _calculate_age(birth_date) -> int:
    """Calculate age from birth date."""
    today = datetime.date.today()
    return (
        today.year - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )
