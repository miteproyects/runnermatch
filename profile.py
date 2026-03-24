"""
RunnerMatch - User Profile Management
Manages user profiles and runner certification.
"""


def create_profile(uid: str) -> dict:
    """Create a new profile for a user."""
    return {
        "uid": uid,
        "created_at": now,
        "verified": False,
        "evidence_urls": [],
        "docs_verified": []
        