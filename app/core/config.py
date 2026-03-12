"""
Config
======
All hardcoded constants for the application.
No environment variables here — those live in settings.py.

Usage:
    from app.core.config import RAGConfig, TrialConfig, PathConfig
"""

from pathlib import Path

# ── Project paths ─────────────────────────────────────────────────────────────
class PathConfig:
    ROOT_DIR       = Path(__file__).resolve().parents[2]
    DATA_DIR       = ROOT_DIR / "data"
    RAW_DIR        = DATA_DIR / "raw"
    PROCESSED_DIR  = DATA_DIR / "processed"
    VECTOR_DB_DIR  = DATA_DIR / "vector_db"
    LOG_FILE       = DATA_DIR / "question_log.json"


# ── RAG pipeline ──────────────────────────────────────────────────────────────
class RAGConfig:
    CHUNK_SIZE     = 500    # characters per chunk
    CHUNK_OVERLAP  = 75     # overlap between chunks
    TOP_K          = 4      # number of chunks to retrieve per query
    SEPARATORS     = ["\n\n", "\n", ". ", " ", ""]


# ── LLM ───────────────────────────────────────────────────────────────────────
class LLMConfig:
    TEMPERATURE       = 0.7
    MAX_TOKENS        = 600
    TOPIC_TEMPERATURE = 0.0
    TOPIC_MAX_TOKENS  = 15


# ── Trial system ──────────────────────────────────────────────────────────────
class TrialConfig:
    TRIAL_LIMIT           = 3
    RATE_WINDOW_SECONDS   = 3600   # 1-hour window per IP

    ACCESS_CODES: set[str] = {
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


# ── Max persona ───────────────────────────────────────────────────────────────
class PromptConfig:
    SYSTEM_PROMPT = """You are Money Coach Max, a warm and encouraging financial coach.

Your knowledge comes from Rich Dad Poor Dad and curated financial education materials.
You help everyday families understand personal finance in simple, practical terms.

PERSONALITY:
- Friendly, encouraging, conversational — like a trusted friend who knows money
- Use plain language, avoid financial jargon
- Give practical, actionable advice
- Acknowledge that money is stressful — be empathetic

STRICT GUARDRAILS — you NEVER:
- Recommend specific stocks, funds, or investments ("buy X")
- Give tax advice ("you should deduct Y")
- Give legal advice of any kind
- Recommend specific financial products or institutions
- Guarantee financial outcomes

If asked about investments, taxes, or legal matters, respond with:
"For personalized advice on that, I'd recommend speaking with a certified
financial advisor or tax professional — they can look at your full picture."

FORMAT RULES:
- Keep responses to 3–5 short paragraphs
- End every response with ONE follow-up question
- Be specific — reference concepts from the knowledge base when relevant

KNOWLEDGE BASE CONTEXT:
{context}
"""

    TOPIC_PROMPT = (
        "In 2–4 words, what financial topic is this question about?\n"
        "Question: '{question}'\n"
        "Reply with ONLY the topic label, nothing else."
    )