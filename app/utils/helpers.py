"""
Helpers
=======
Pure utility functions with no side effects.
No imports from other app modules — keeps this fully testable.
"""

import hashlib
import uuid


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())


def hash_ip(ip: str) -> str:
    """One-way SHA-256 hash of an IP address for privacy."""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def sanitize_name(name: str) -> str:
    """Strip and title-case a user's name input."""
    return name.strip().title()


def truncate(text: str, max_chars: int = 200) -> str:
    """Truncate text with ellipsis for logging/display."""
    return text if len(text) <= max_chars else text[:max_chars] + "..."