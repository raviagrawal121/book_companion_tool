"""
Logger
======
Anonymously logs every question with a topic tag.
v1: JSON file on disk
v2: swap _load/_save for SQLAlchemy + PostgreSQL

Usage:
    from app.utils.logger import log_question, get_logs
    log_question("How do I save money?", "budgeting")
"""

import json
from datetime import datetime, timezone
from app.core.config import PathConfig


def log_question(question: str, topic: str) -> None:
    """Append an anonymised question entry to the log."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question":  question,
        "topic":     topic,
    }
    logs = get_logs()
    logs.append(entry)
    _save(logs)


def get_logs() -> list[dict]:
    """Return all logged questions."""
    return _load()


def _load() -> list[dict]:
    if not PathConfig.LOG_FILE.exists():
        return []
    try:
        return json.loads(PathConfig.LOG_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _save(logs: list[dict]) -> None:
    PathConfig.DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        PathConfig.LOG_FILE.write_text(json.dumps(logs, indent=2))
    except OSError as e:
        print(f"[logger] Write failed: {e}")