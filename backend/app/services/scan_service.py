"""
Sentinel AI — Scan Service

Orchestrates the full scan workflow: detection → sanitization → storage → analytics.
"""

import logging
from typing import Optional

from app.database.connection import get_database
from app.detection.engine import DetectionEngine
from app.models.scan import ScanModel, ScanResult, ThreatMatch
from app.utils.helpers import generate_id, utc_now, today_str

logger = logging.getLogger("sentinel.scan_service")

# Singleton engine instance
_engine = DetectionEngine()


async def scan_prompt(prompt: str, user_id: str, target_llm: Optional[str] = None) -> dict:
    """
    Run the full scan pipeline on a prompt.

    1. Run detection engine
    2. Build scan record
    3. Store in MongoDB
    4. Update user stats
    5. Update daily analytics

    Returns:
        Scan result dict ready for API response.
    """
    db = get_database()

    # Run detection
    analysis = await _engine.analyze(prompt)

    # Build threat matches
    threat_matches = [
        ThreatMatch(
            category=t["category"],
            severity=t["severity"],
            confidence=t["confidence"],
            matched_text=t["matched_text"],
            explanation=t["explanation"],
        )
        for t in analysis["threat_matches"]
    ]

    # Build scan result
    scan_result = ScanResult(
        risk_score=analysis["risk_score"],
        overall_severity=analysis["overall_severity"],
        is_safe=analysis["is_safe"],
        threats_detected=analysis["threats_detected"],
        threat_matches=threat_matches,
        original_prompt=analysis["original_prompt"],
        sanitized_prompt=analysis["sanitized_prompt"],
        target_llm=target_llm,
    )

    # Build scan model
    scan = ScanModel(
        _id=generate_id(),
        user_id=user_id,
        prompt=prompt,
        target_llm=target_llm,
        result=scan_result,
        created_at=utc_now(),
    )

    # Store scan record
    await db.scans.insert_one(scan.to_mongo())

    # Update user stats
    update_fields = {"$inc": {"total_scans": 1}}
    if not analysis["is_safe"]:
        update_fields["$inc"]["threats_blocked"] = 1
    await db.users.update_one({"_id": user_id}, update_fields)

    # Update daily analytics
    await _update_daily_analytics(db, user_id, analysis)

    logger.info(
        "Scan completed: user=%s risk=%.1f threats=%d safe=%s",
        user_id, analysis["risk_score"], analysis["threats_detected"], analysis["is_safe"],
    )

    return scan.to_response()


async def get_scan_by_id(scan_id: str, user_id: str) -> Optional[dict]:
    """Fetch a specific scan by ID, scoped to user."""
    db = get_database()
    scan = await db.scans.find_one({"_id": scan_id, "user_id": user_id})
    if scan:
        scan["id"] = scan.pop("_id")
    return scan


async def get_scan_history(user_id: str, page: int = 1, page_size: int = 20) -> dict:
    """Fetch paginated scan history for a user."""
    db = get_database()
    skip = (page - 1) * page_size

    total = await db.scans.count_documents({"user_id": user_id})
    cursor = db.scans.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(page_size)

    scans = []
    async for doc in cursor:
        doc["id"] = doc.pop("_id")
        scans.append(doc)

    total_pages = max(1, (total + page_size - 1) // page_size)

    return {
        "scans": scans,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


async def _update_daily_analytics(db, user_id: str, analysis: dict) -> None:
    """Update or create the daily analytics document."""
    date = today_str()
    threats_count = analysis["threats_detected"]
    is_blocked = not analysis["is_safe"]

    # Gather category counts
    category_increments = {}
    for threat in analysis["threat_matches"]:
        cat = threat["category"]
        category_increments[f"threat_categories.{cat}"] = category_increments.get(
            f"threat_categories.{cat}", 0
        ) + 1

    # Severity increments
    severity_increments = {}
    for threat in analysis["threat_matches"]:
        sev = threat["severity"]
        severity_increments[f"severity_distribution.{sev}"] = severity_increments.get(
            f"severity_distribution.{sev}", 0
        ) + 1

    update = {
        "$inc": {
            "total_scans": 1,
            "threats_detected": threats_count,
            "attacks_blocked": 1 if is_blocked else 0,
            **category_increments,
            **severity_increments,
        },
        "$max": {"max_risk_score": analysis["risk_score"]},
        "$setOnInsert": {
            "_id": generate_id(),
            "user_id": user_id,
            "date": date,
            "created_at": utc_now(),
        },
        "$set": {"updated_at": utc_now()},
    }

    await db.analytics.update_one(
        {"user_id": user_id, "date": date},
        update,
        upsert=True,
    )
