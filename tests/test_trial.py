"""
Tests — Trial Service
=====================
Tests for question limits, IP rate limiting, and access code validation.
No external dependencies.
"""

import pytest
from app.services.session_service import SessionService
from app.services.trial_service import TrialService


def fresh_session() -> str:
    """Return a unique session ID for each test."""
    import uuid
    return str(uuid.uuid4())


# ── Trial limit ───────────────────────────────────────────────────────────────

def test_can_ask_initially_allowed():
    sid = fresh_session()
    allowed, reason = TrialService.can_ask(sid, "1.2.3.4")
    assert allowed is True
    assert reason == "ok"


def test_trial_blocks_after_limit():
    sid = fresh_session()
    ip  = "10.0.0.99"

    for _ in range(3):
        allowed, _ = TrialService.can_ask(sid, ip)
        assert allowed
        TrialService.record_question(sid, ip)

    allowed, reason = TrialService.can_ask(sid, ip)
    assert allowed is False
    assert reason == "trial_limit"


def test_questions_remaining_counts_down():
    sid = fresh_session()
    ip  = "10.0.0.50"

    assert TrialService.questions_remaining(sid) == 3
    TrialService.record_question(sid, ip)
    assert TrialService.questions_remaining(sid) == 2
    TrialService.record_question(sid, ip)
    assert TrialService.questions_remaining(sid) == 1


# ── Access codes ──────────────────────────────────────────────────────────────

def test_valid_code_unlocks_session():
    sid = fresh_session()
    result = TrialService.verify_code(sid, "STORM2026")
    assert result is True
    assert SessionService.is_unlocked(sid) is True


def test_invalid_code_rejected():
    sid = fresh_session()
    result = TrialService.verify_code(sid, "BADCODE123")
    assert result is False
    assert SessionService.is_unlocked(sid) is False


def test_code_case_insensitive():
    sid = fresh_session()
    result = TrialService.verify_code(sid, "storm2026")
    assert result is True


def test_unlocked_session_bypasses_limit():
    sid = fresh_session()
    ip  = "10.0.0.77"

    # Exhaust trial
    for _ in range(3):
        TrialService.record_question(sid, ip)

    # Unlock
    TrialService.verify_code(sid, "MAX2026")

    # Should now be allowed
    allowed, reason = TrialService.can_ask(sid, ip)
    assert allowed is True
    assert reason == "ok"