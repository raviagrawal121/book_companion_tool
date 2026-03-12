"""
Session Models
==============
Pydantic schemas for session management endpoints.
"""

from pydantic import BaseModel, Field


class NewSessionResponse(BaseModel):
    session_id: str


class SetNameRequest(BaseModel):
    session_id: str
    name: str = Field(..., min_length=1, max_length=50)


class SetNameResponse(BaseModel):
    ok:   bool
    name: str


class SessionStatusResponse(BaseModel):
    name:                str
    question_count:      int
    questions_remaining: int
    unlocked:            bool


class QuestionLogEntry(BaseModel):
    timestamp: str
    question:  str
    topic:     str


class LogsResponse(BaseModel):
    total: int
    logs:  list[QuestionLogEntry]