"""
Anonymous question logger — stores questions with AI-generated topic tags
In demo: writes to a local JSON file. In production: PostgreSQL.
"""

import json
import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "../data/question_log.json")


def log_question(question: str, topic: str) -> None:
    """Append a question log entry."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "topic": topic,
    }
    logs = _load_logs()
    logs.append(entry)
    try:
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Logger error: {e}")


def get_logs() -> list[dict]:
    return _load_logs()


def _load_logs() -> list[dict]:
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []
