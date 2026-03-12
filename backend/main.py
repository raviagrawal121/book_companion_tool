"""
Book Companion Tool — FastAPI Backend
Run with: uvicorn main:app --reload --port 8000
"""

import os
import uuid
import random
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

from rag.engine import load_documents, retrieve
from services.session import (
    get_session, set_name, can_ask, increment_count,
    verify_code, is_unlocked, VALID_CODES
)
from services.logger import log_question

# ── OpenAI client ────────────────────────────────────────────────────────────
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── Document paths ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
DOCUMENTS = [
    os.path.join(BASE_DIR, "data/rdpd_content.txt"),
]


# ── Startup: load RAG documents ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_documents(DOCUMENTS)
    yield

app = FastAPI(title="Money Coach Max API", lifespan=lifespan)

# ── CORS (allow Wix + local dev) ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your Wix domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── System prompt for Max ─────────────────────────────────────────────────────
MAX_SYSTEM_PROMPT = """You are Book Companion Tool, a friendly and encouraging financial coach assistant.

Your role is to help families and households understand personal finance concepts in a simple, 
practical, and supportive way. You use knowledge from Rich Dad Poor Dad and general financial 
education principles.

PERSONALITY:
- Warm, encouraging, and conversational
- Use simple language — avoid jargon
- Give practical, actionable guidance
- Be empathetic — money is stressful for many families

STRICT BOUNDARIES — you NEVER:
- Give specific investment advice ("buy this stock")
- Give tax advice ("you should deduct this")
- Give legal advice
- Recommend specific financial products or companies
- Make guarantees about financial outcomes

When users ask about investments, taxes, or legal matters, always say:
"That's a great question — for personalized advice on that, I'd recommend speaking with 
a certified financial advisor or tax professional."

Always end responses with one follow-up question to keep the conversation going.
Keep responses to 3-5 paragraphs maximum — clear and digestible.

Use the provided context from our knowledge base to answer questions. If the context 
doesn't cover something, use your general financial education knowledge but stay within 
the boundaries above.
"""


# ── Request/Response schemas ──────────────────────────────────────────────────
class SetNameRequest(BaseModel):
    session_id: str
    name: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

class VerifyCodeRequest(BaseModel):
    session_id: str
    code: str

class VerifyPurchaseRequest(BaseModel):
    session_id: str
    first_name: str
    email: str
    order_number: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "Money Coach Max is running 🚀"}


@app.post("/session/new")
def new_session():
    """Generate a new session ID for a visitor."""
    return {"session_id": str(uuid.uuid4())}


@app.post("/session/name")
def set_user_name(body: SetNameRequest):
    """Store the user's first name for the session."""
    set_name(body.session_id, body.name.strip())
    return {"ok": True, "name": body.name.strip()}


@app.get("/session/status")
def session_status(session_id: str):
    """Return current session state."""
    session = get_session(session_id)
    return {
        "name": session.get("name", ""),
        "question_count": session.get("count", 0),
        "unlocked": session.get("unlocked", False),
        "questions_remaining": max(0, 3 - session.get("count", 0)),
    }


@app.post("/chat")
async def chat(body: ChatRequest, request: Request):
    """Main chat endpoint — RAG + OpenAI streaming response."""
    client_ip = request.client.host
    session_id = body.session_id

    # Check if user can ask
    allowed, reason = can_ask(session_id, client_ip)
    if not allowed:
        return {
            "blocked": True,
            "reason": reason,
            "message": (
                "You've used your 3 free questions! "
                "Readers of the book get unlimited access to Max. "
                "Enter your access code below to continue."
            )
        }

    # Retrieve relevant context from RAG
    context_chunks = retrieve(body.message, top_k=4)
    context = "\n\n---\n\n".join(context_chunks)

    # Get user name for personalization
    session = get_session(session_id)
    user_name = session.get("name", "there")

    # Build messages
    messages = [
        {"role": "system", "content": MAX_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""KNOWLEDGE BASE CONTEXT:
{context}

---
USER ({user_name}) ASKS: {body.message}

Please answer based on the context above and your financial coaching knowledge."""
        }
    ]

    # Increment count BEFORE calling API (prevents gaming)
    new_count = increment_count(session_id, client_ip)
    questions_remaining = max(0, 3 - new_count)

    # Call OpenAI (non-streaming for simplicity in demo)
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=600,
    )

    answer = response.choices[0].message.content

    # AI-generated topic tag for logging
    topic_response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"In 2-4 words, what financial topic is this question about? Question: '{body.message}'. Reply with ONLY the topic label."
        }],
        max_tokens=15,
        temperature=0,
    )
    topic = topic_response.choices[0].message.content.strip()

    # Log anonymously
    log_question(body.message, topic)

    # Trial end message
    trial_message = None
    if new_count >= 3 and not is_unlocked(session_id):
        trial_message = (
            "I hope that was helpful! 😊 You've used your 3 free questions. "
            "Book readers get unlimited access to Max — enter your access code below to continue!"
        )

    return {
        "blocked": False,
        "answer": answer,
        "question_count": new_count,
        "questions_remaining": questions_remaining,
        "trial_ended": new_count >= 3 and not is_unlocked(session_id),
        "trial_message": trial_message,
        "topic": topic,
    }


@app.post("/verify/code")
def verify_access_code(body: VerifyCodeRequest):
    """Verify an access code and unlock the session."""
    success = verify_code(body.session_id, body.code)
    return {
        "success": success,
        "message": (
            "✅ Access granted! Welcome to unlimited Max access."
            if success else
            "❌ That code doesn't seem right. Double-check and try again."
        )
    }


@app.post("/verify/purchase")
def verify_purchase(body: VerifyPurchaseRequest):
    """Handle book purchase verification form and return a random access code."""
    # In production: store this in a DB and manually/auto verify
    # For demo: just return a random code
    code = random.choice(list(VALID_CODES))
    print(f"📬 Purchase verification: {body.first_name} | {body.email} | Order: {body.order_number} → Code: {code}")
    return {
        "success": True,
        "code": code,
        "message": f"Thanks {body.first_name}! Here's your personal access code:"
    }


@app.get("/admin/logs")
def get_question_logs():
    """Admin endpoint — view anonymous question log."""
    from services.logger import get_logs
    logs = get_logs()
    return {"total": len(logs), "logs": logs}


# ── Init files ────────────────────────────────────────────────────────────────
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
for pkg in ["rag", "services"]:
    init = os.path.join(BASE_DIR, pkg, "__init__.py")
    if not os.path.exists(init):
        open(init, "w").close()
