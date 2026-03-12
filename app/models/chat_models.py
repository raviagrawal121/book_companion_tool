"""
Chat Models
===========
Pydantic schemas for chat request/response.
FastAPI uses these for automatic validation and OpenAPI docs.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from /session/new")
    message: str    = Field(..., min_length=1, max_length=1000,
                            description="User's question to Max")

    model_config = {"json_schema_extra": {
        "example": {
            "session_id": "abc-123",
            "message": "What is the difference between an asset and a liability?"
        }
    }}


class ChatResponse(BaseModel):
    blocked:             bool
    answer:              Optional[str]       = None
    question_count:      Optional[int]       = None
    questions_remaining: Optional[int]       = None
    trial_ended:         Optional[bool]      = None
    trial_message:       Optional[str]       = None
    topic:               Optional[str]       = None
    sources:             Optional[list[str]] = None  # page references shown to user


class VerifyCodeRequest(BaseModel):
    session_id: str
    code: str = Field(..., min_length=1, max_length=30)


class VerifyCodeResponse(BaseModel):
    success: bool
    message: str


class VerifyPurchaseRequest(BaseModel):
    session_id:   str
    first_name:   str = Field(..., min_length=1, max_length=50)
    email:        str
    order_number: str = Field(..., min_length=3, max_length=50)


class VerifyPurchaseResponse(BaseModel):
    success: bool
    code:    str
    message: str