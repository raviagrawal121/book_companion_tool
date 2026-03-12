"""
Tests — Chat API
================
Integration tests for all API endpoints using FastAPI TestClient.
Mocks the ChatService so no real OpenAI or FAISS calls are made.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── Session endpoints ─────────────────────────────────────────────────────────

def test_new_session_returns_id():
    res = client.post("/session/new")
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    assert len(data["session_id"]) > 0


def test_set_name_and_get_status():
    # Create session
    sid = client.post("/session/new").json()["session_id"]

    # Set name
    res = client.post("/session/name", json={"session_id": sid, "name": "Sarah"})
    assert res.status_code == 200
    assert res.json()["name"] == "Sarah"

    # Check status
    res = client.get(f"/session/status?session_id={sid}")
    data = res.json()
    assert data["name"] == "Sarah"
    assert data["question_count"] == 0
    assert data["questions_remaining"] == 3
    assert data["unlocked"] is False


# ── Chat endpoint ─────────────────────────────────────────────────────────────

MOCK_CHAT_RESULT = {
    "blocked":             False,
    "answer":              "Assets put money in your pocket!",
    "question_count":      1,
    "questions_remaining": 2,
    "trial_ended":         False,
    "trial_message":       None,
    "topic":               "assets vs liabilities",
    "sources":             ["rdpd_book.pdf p.12"],
}


@patch("app.api.chat.ChatService.ask", return_value=MOCK_CHAT_RESULT)
def test_chat_returns_answer(mock_ask):
    sid = client.post("/session/new").json()["session_id"]
    res = client.post("/chat", json={"session_id": sid, "message": "What is an asset?"})
    assert res.status_code == 200
    data = res.json()
    assert data["blocked"] is False
    assert "Assets" in data["answer"]
    assert data["topic"] == "assets vs liabilities"


def test_chat_missing_message_rejected():
    sid = client.post("/session/new").json()["session_id"]
    res = client.post("/chat", json={"session_id": sid, "message": ""})
    assert res.status_code == 422   # Pydantic validation error


# ── Access code verification ──────────────────────────────────────────────────

def test_valid_access_code():
    sid = client.post("/session/new").json()["session_id"]
    res = client.post("/verify/code", json={"session_id": sid, "code": "STORM2026"})
    assert res.status_code == 200
    assert res.json()["success"] is True


def test_invalid_access_code():
    sid = client.post("/session/new").json()["session_id"]
    res = client.post("/verify/code", json={"session_id": sid, "code": "WRONGCODE"})
    assert res.status_code == 200
    assert res.json()["success"] is False


# ── Purchase verification ─────────────────────────────────────────────────────

def test_purchase_verification_returns_code():
    sid = client.post("/session/new").json()["session_id"]
    res = client.post("/verify/purchase", json={
        "session_id":   sid,
        "first_name":   "Sarah",
        "email":        "sarah@example.com",
        "order_number": "113-1234567-8901234",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["code"]) > 0


# ── Health check ──────────────────────────────────────────────────────────────

def test_health_check():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "running"