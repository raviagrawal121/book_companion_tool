"""
Session management — trial question tracking + access code verification
Uses in-memory store for demo (swap for Redis/DB in production)
"""

import time
import hashlib
from collections import defaultdict

# ── Predefined access codes (client will provide their own) ─────────────────
VALID_CODES = {
    "STORM2026",
    "MAX2026",
    "JOEPLAN",
    "SAFESEAS",
    "SMARTMONEY",
    "RICHLIFE",
    "MONEYMAX",
    "FREEDOM26",
    "COACHMAX",
    "WEALTHIQ",
}

# ── In-memory session store (keyed by session_id) ───────────────────────────
# Structure: { session_id: { "count": int, "unlocked": bool, "name": str } }
_sessions: dict[str, dict] = defaultdict(lambda: {"count": 0, "unlocked": False, "name": ""})

# ── IP-based rate limiting ────────────────────────────────────────────────── 
# Structure: { ip_hash: { "count": int, "window_start": float } }
_ip_store: dict[str, dict] = {}
TRIAL_LIMIT = 3
RATE_WINDOW_SECONDS = 3600  # 1 hour window


def _hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def get_session(session_id: str) -> dict:
    return _sessions[session_id]


def set_name(session_id: str, name: str) -> None:
    _sessions[session_id]["name"] = name


def can_ask(session_id: str, ip: str) -> tuple[bool, str]:
    """Check if user can ask another question. Returns (allowed, reason)."""
    session = _sessions[session_id]

    # Unlocked users have unlimited access
    if session.get("unlocked"):
        return True, "unlocked"

    # Check session question count
    if session["count"] >= TRIAL_LIMIT:
        return False, "trial_limit"

    # Check IP rate limiting
    ip_hash = _hash_ip(ip)
    now = time.time()
    ip_data = _ip_store.get(ip_hash, {"count": 0, "window_start": now})

    # Reset window if expired
    if now - ip_data["window_start"] > RATE_WINDOW_SECONDS:
        ip_data = {"count": 0, "window_start": now}

    if ip_data["count"] >= TRIAL_LIMIT:
        return False, "ip_limit"

    return True, "ok"


def increment_count(session_id: str, ip: str) -> int:
    """Increment question count. Returns new count."""
    _sessions[session_id]["count"] += 1

    ip_hash = _hash_ip(ip)
    now = time.time()
    ip_data = _ip_store.get(ip_hash, {"count": 0, "window_start": now})
    if now - ip_data["window_start"] > RATE_WINDOW_SECONDS:
        ip_data = {"count": 0, "window_start": now}
    ip_data["count"] += 1
    _ip_store[ip_hash] = ip_data

    return _sessions[session_id]["count"]


def verify_code(session_id: str, code: str) -> bool:
    """Verify access code and unlock session if valid."""
    if code.strip().upper() in VALID_CODES:
        _sessions[session_id]["unlocked"] = True
        return True
    return False


def is_unlocked(session_id: str) -> bool:
    return _sessions[session_id].get("unlocked", False)
