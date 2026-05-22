"""
Sentinel AI — Utility Helpers

Common utility functions used across the application.
"""

import uuid
from datetime import datetime, timezone


def generate_id() -> str:
    """Generate a unique string ID for MongoDB documents."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def today_str() -> str:
    """Return today's date as YYYY-MM-DD string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def severity_from_score(score: float) -> str:
    """
    Map a 0-100 risk score to a severity label.

    0-25   → LOW
    26-50  → MEDIUM
    51-75  → HIGH
    76-100 → CRITICAL
    """
    if score <= 25:
        return "LOW"
    elif score <= 50:
        return "MEDIUM"
    elif score <= 75:
        return "HIGH"
    else:
        return "CRITICAL"


SEVERITY_MULTIPLIER = {
    "LOW": 1.0,
    "MEDIUM": 2.0,
    "HIGH": 3.0,
    "CRITICAL": 4.0,
}
