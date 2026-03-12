"""
Session Service
===============
Manages per-visitor session state stored in memory.
Tracks: name, question count, unlocked status.

In production (v2): replace _sessions dict with Redis.

Usage:
    from app.services.session_service import SessionService
    SessionService.set_name(session_id, "Sarah")
    state = SessionService.get(session_id)
"""

from collections import defaultdict


# In-memory store: { session_id: { name, count, unlocked } }
_sessions: dict[str, dict] = defaultdict(
    lambda: {"name": "", "count": 0, "unlocked": False}
)


class SessionService:

    @staticmethod
    def get(session_id: str) -> dict:
        """Return the full session dict for a given ID."""
        return _sessions[session_id]

    @staticmethod
    def set_name(session_id: str, name: str) -> None:
        """Store the user's first name in their session."""
        _sessions[session_id]["name"] = name.strip()

    @staticmethod
    def get_name(session_id: str) -> str:
        return _sessions[session_id].get("name", "there")

    @staticmethod
    def is_unlocked(session_id: str) -> bool:
        return _sessions[session_id].get("unlocked", False)

    @staticmethod
    def unlock(session_id: str) -> None:
        """Grant unlimited access to a session."""
        _sessions[session_id]["unlocked"] = True

    @staticmethod
    def get_count(session_id: str) -> int:
        return _sessions[session_id].get("count", 0)

    @staticmethod
    def increment_count(session_id: str) -> int:
        """Increment question count and return the new value."""
        _sessions[session_id]["count"] += 1
        return _sessions[session_id]["count"]