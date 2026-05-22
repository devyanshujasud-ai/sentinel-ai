"""
Sentinel AI — Threat Service

Manages threat definitions — seeding, lookup, and CRUD.
"""

import logging
from typing import Optional, List

from app.database.connection import get_database
from app.models.threat import ThreatDefinition
from app.utils.helpers import generate_id, utc_now

logger = logging.getLogger("sentinel.threat_service")

# Default threat definitions seeded on first run
DEFAULT_THREATS = [
    {
        "category": "PROMPT_INJECTION",
        "name": "Prompt Injection",
        "description": "Attempts to override, ignore, or manipulate system instructions given to the LLM.",
        "severity": "CRITICAL",
        "examples": ["ignore previous instructions", "disregard above", "new instructions:"],
        "weight": 0.95,
    },
    {
        "category": "JAILBREAK",
        "name": "Jailbreak Attempt",
        "description": "Attempts to bypass LLM safety guidelines using DAN, role-playing, or constraint removal.",
        "severity": "CRITICAL",
        "examples": ["DAN mode", "developer mode", "act without restrictions"],
        "weight": 0.95,
    },
    {
        "category": "SQL_INJECTION",
        "name": "SQL Injection",
        "description": "SQL injection patterns embedded in prompts to trick LLMs into generating malicious queries.",
        "severity": "HIGH",
        "examples": ["DROP TABLE", "' OR 1=1", "UNION SELECT"],
        "weight": 0.85,
    },
    {
        "category": "SHELL_COMMAND",
        "name": "Dangerous Shell Commands",
        "description": "Destructive shell or system commands that could cause data loss or system compromise.",
        "severity": "CRITICAL",
        "examples": ["sudo rm -rf /", "chmod 777", "curl | bash"],
        "weight": 0.90,
    },
    {
        "category": "TOXICITY",
        "name": "Toxic Content",
        "description": "Requests for violent, hateful, abusive, or illegal content generation.",
        "severity": "HIGH",
        "examples": ["make a bomb", "death threat", "generate hate speech"],
        "weight": 0.75,
    },
    {
        "category": "DATA_LEAKAGE",
        "name": "Sensitive Data Leakage",
        "description": "Prompts containing or requesting extraction of sensitive personal or credential data.",
        "severity": "HIGH",
        "examples": ["my SSN is", "credit card number", "API key"],
        "weight": 0.85,
    },
    {
        "category": "UNSAFE_CODE",
        "name": "Unsafe Code Generation",
        "description": "Requests to generate malware, exploits, or dangerous code patterns.",
        "severity": "HIGH",
        "examples": ["write a virus", "create a keylogger", "buffer overflow exploit"],
        "weight": 0.80,
    },
    {
        "category": "ROLE_MANIPULATION",
        "name": "Role Manipulation",
        "description": "Attempts to extract system prompts or manipulate the LLM's assigned role.",
        "severity": "HIGH",
        "examples": ["reveal system prompt", "act as root", "show me your instructions"],
        "weight": 0.85,
    },
]


async def seed_threats() -> None:
    """Seed default threat definitions if the collection is empty."""
    db = get_database()
    count = await db.threats.count_documents({})
    if count > 0:
        logger.info("Threats collection already seeded (%d documents).", count)
        return

    docs = []
    for t in DEFAULT_THREATS:
        threat = ThreatDefinition(
            _id=generate_id(),
            category=t["category"],
            name=t["name"],
            description=t["description"],
            severity=t["severity"],
            examples=t["examples"],
            weight=t["weight"],
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        docs.append(threat.to_mongo())

    await db.threats.insert_many(docs)
    logger.info("Seeded %d default threat definitions.", len(docs))


async def get_all_threats() -> List[dict]:
    """Fetch all active threat definitions."""
    db = get_database()
    cursor = db.threats.find({"is_active": True}).sort("category", 1)
    threats = []
    async for doc in cursor:
        doc["id"] = doc.pop("_id")
        threats.append(doc)
    return threats


async def get_threats_by_category(category: str) -> List[dict]:
    """Fetch threats by category."""
    db = get_database()
    cursor = db.threats.find({"category": category.upper(), "is_active": True})
    threats = []
    async for doc in cursor:
        doc["id"] = doc.pop("_id")
        threats.append(doc)
    return threats
