"""
API Router — chat.py
====================
All Money Coach Max endpoints.
Kept deliberately thin — validation + service call + return.
No business logic lives here.
"""

import uuid
from fastapi import APIRouter, Request

from app.models.chat_models import (
    ChatRequest, ChatResponse,
    VerifyCodeRequest, VerifyCodeResponse,
    VerifyPurchaseRequest, VerifyPurchaseResponse,
)
from app.models.session_models import (
    NewSessionResponse, SetNameRequest, SetNameResponse,
    SessionStatusResponse, LogsResponse,
)
from app.services.session_service import SessionService
from app.services.trial_service import TrialService
from app.services.chat_service import ChatService
from app.utils.logger import get_logs
from app.core.config import TrialConfig

router = APIRouter()


# ── Session endpoints ─────────────────────────────────────────────────────────

@router.post(
    "/session/new",
    response_model=NewSessionResponse,
    summary="Create a new visitor session",
)
def new_session():
    return NewSessionResponse(session_id=str(uuid.uuid4()))


@router.post(
    "/session/name",
    response_model=SetNameResponse,
    summary="Set the user's first name",
)
def set_name(body: SetNameRequest):
    SessionService.set_name(body.session_id, body.name)
    return SetNameResponse(ok=True, name=body.name.strip())


@router.get(
    "/session/status",
    response_model=SessionStatusResponse,
    summary="Get current session state",
)
def session_status(session_id: str):
    return SessionStatusResponse(
        name=SessionService.get_name(session_id),
        question_count=SessionService.get_count(session_id),
        questions_remaining=TrialService.questions_remaining(session_id),
        unlocked=SessionService.is_unlocked(session_id),
    )


# ── Chat endpoint ─────────────────────────────────────────────────────────────

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a message to Money Coach Max",
)
def chat(body: ChatRequest, request: Request):
    """
    Core RAG chat endpoint.
    Retrieves relevant book content, assembles prompt, returns Max's response.
    """
    client_ip = request.client.host
    result    = ChatService.ask(body.session_id, body.message, client_ip)
    return ChatResponse(**result)


# ── Access code verification ──────────────────────────────────────────────────

@router.post(
    "/verify/code",
    response_model=VerifyCodeResponse,
    summary="Validate an access code",
)
def verify_code(body: VerifyCodeRequest):
    success = TrialService.verify_code(body.session_id, body.code)
    return VerifyCodeResponse(
        success=success,
        message=(
            "✅ Access granted! Welcome to unlimited Max access."
            if success else
            "❌ That code doesn't look right — double-check and try again."
        ),
    )


@router.post(
    "/verify/purchase",
    response_model=VerifyPurchaseResponse,
    summary="Submit Amazon purchase for verification",
)
def verify_purchase(body: VerifyPurchaseRequest):
    result = ChatService.verify_purchase(
        body.first_name, body.email, body.order_number
    )
    return VerifyPurchaseResponse(**result)


# ── Admin ─────────────────────────────────────────────────────────────────────

@router.get(
    "/admin/logs",
    response_model=LogsResponse,
    summary="View anonymised question log",
)
def get_question_logs():
    logs = get_logs()
    return LogsResponse(total=len(logs), logs=logs)