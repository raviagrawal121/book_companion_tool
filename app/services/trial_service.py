"""
Trial Service
=============
Enforces the 3-question trial limit using:
  - Session-level counter (per browser session)
  - IP-level rate limiting (prevents session refresh gaming)

Also handles access code validation.

Usage:
    from app.services.trial_service import TrialService
    allowed, reason = TrialService.can_ask(session_id, client_ip)
"""

import time
import hashlib

from app.core.config import TrialConfig
from app.services.session_service import SessionService


# IP rate limit store: { ip_hash: { count, window_start } }
_ip_store: dict[str, dict] = {}


class TrialService:

    @staticmethod
    def _hash_ip(ip: str) -> str:
        """One-way hash the IP address for privacy."""
        return hashlib.sha256(ip.encode()).hexdigest()[:16]

    @staticmethod
    def can_ask(session_id: str, ip: str) -> tuple[bool, str]:
        """
        Check whether a user is allowed to ask another question.

        Returns:
            (True,  "ok")           — allowed
            (False, "trial_limit")  — session exhausted
            (False, "ip_limit")     — IP exhausted within rate window
        """
        # Unlocked users always get through
        if SessionService.is_unlocked(session_id):
            return True, "ok"

        # Session-level check
        if SessionService.get_count(session_id) >= TrialConfig.TRIAL_LIMIT:
            return False, "trial_limit"

        # IP-level check (catch session refresh attempts)
        ip_hash = TrialService._hash_ip(ip)
        now     = time.time()
        ip_data = _ip_store.get(ip_hash, {"count": 0, "window_start": now})

        # Reset window if expired
        if now - ip_data["window_start"] > TrialConfig.RATE_WINDOW_SECONDS:
            ip_data = {"count": 0, "window_start": now}

        if ip_data["count"] >= TrialConfig.TRIAL_LIMIT:
            return False, "ip_limit"

        return True, "ok"

    @staticmethod
    def record_question(session_id: str, ip: str) -> int:
        """
        Increment both session and IP counters after a question is answered.
        Returns the new session question count.
        """
        # Increment session counter
        new_count = SessionService.increment_count(session_id)

        # Increment IP counter
        ip_hash = TrialService._hash_ip(ip)
        now     = time.time()
        ip_data = _ip_store.get(ip_hash, {"count": 0, "window_start": now})

        if now - ip_data["window_start"] > TrialConfig.RATE_WINDOW_SECONDS:
            ip_data = {"count": 0, "window_start": now}

        ip_data["count"]  += 1
        _ip_store[ip_hash] = ip_data

        return new_count

    @staticmethod
    def verify_code(session_id: str, code: str) -> bool:
        """
        Validate an access code (case-insensitive).
        Unlocks the session if valid.
        Returns True if code is valid.
        """
        if code.strip().upper() in TrialConfig.ACCESS_CODES:
            SessionService.unlock(session_id)
            return True
        return False

    @staticmethod
    def questions_remaining(session_id: str) -> int:
        """How many trial questions does this session have left?"""
        if SessionService.is_unlocked(session_id):
            return 999  # unlimited
        return max(0, TrialConfig.TRIAL_LIMIT - SessionService.get_count(session_id))