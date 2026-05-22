"""
Sentinel AI — Analytics Service

Aggregation queries for dashboard stats, top threats, risk trends, and daily statistics.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from app.database.connection import get_database
from app.utils.helpers import today_str


async def get_dashboard_stats(user_id: str) -> dict:
    """Get overall dashboard summary statistics."""
    db = get_database()

    total_scans = await db.scans.count_documents({"user_id": user_id})
    unsafe_scans = await db.scans.count_documents(
        {"user_id": user_id, "result.is_safe": False}
    )
    safe_scans = total_scans - unsafe_scans

    # Calculate total threats and average risk
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": None,
                "total_threats": {"$sum": "$result.threats_detected"},
                "avg_risk": {"$avg": "$result.risk_score"},
            }
        },
    ]
    result = await db.scans.aggregate(pipeline).to_list(1)

    if result:
        total_threats = result[0].get("total_threats", 0)
        avg_risk = round(result[0].get("avg_risk", 0), 2)
    else:
        total_threats = 0
        avg_risk = 0.0

    return {
        "total_scans": total_scans,
        "threats_detected": total_threats,
        "attacks_blocked": unsafe_scans,
        "avg_risk_score": avg_risk,
        "safe_prompts": safe_scans,
        "unsafe_prompts": unsafe_scans,
    }


async def get_top_threats(user_id: str, limit: int = 10) -> dict:
    """Get top threat categories by frequency."""
    db = get_database()

    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$unwind": "$result.threat_matches"},
        {
            "$group": {
                "_id": "$result.threat_matches.category",
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]

    results = await db.scans.aggregate(pipeline).to_list(limit)
    total = sum(r["count"] for r in results)

    threats = [
        {
            "category": r["_id"],
            "count": r["count"],
            "percentage": round((r["count"] / total * 100) if total > 0 else 0, 2),
        }
        for r in results
    ]

    return {"threats": threats, "total_threats": total}


async def get_risk_trends(user_id: str, days: int = 30) -> dict:
    """Get daily risk score trends over a period."""
    db = get_database()
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    pipeline = [
        {"$match": {"user_id": user_id, "created_at": {"$gte": start_date}}},
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                },
                "avg_risk_score": {"$avg": "$result.risk_score"},
                "total_scans": {"$sum": 1},
                "threats_detected": {"$sum": "$result.threats_detected"},
            }
        },
        {"$sort": {"_id": 1}},
    ]

    results = await db.scans.aggregate(pipeline).to_list(days)

    trends = [
        {
            "date": r["_id"],
            "avg_risk_score": round(r["avg_risk_score"], 2),
            "total_scans": r["total_scans"],
            "threats_detected": r["threats_detected"],
        }
        for r in results
    ]

    return {"trends": trends, "period_days": days}


async def get_daily_statistics(user_id: str, days: int = 30) -> dict:
    """Get daily scan and threat statistics."""
    db = get_database()
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    pipeline = [
        {"$match": {"user_id": user_id, "created_at": {"$gte": start_date}}},
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                },
                "scans": {"$sum": 1},
                "threats": {"$sum": "$result.threats_detected"},
                "attacks_blocked": {
                    "$sum": {"$cond": [{"$eq": ["$result.is_safe", False]}, 1, 0]}
                },
                "avg_risk": {"$avg": "$result.risk_score"},
            }
        },
        {"$sort": {"_id": 1}},
    ]

    results = await db.scans.aggregate(pipeline).to_list(days)

    stats = [
        {
            "date": r["_id"],
            "scans": r["scans"],
            "threats": r["threats"],
            "attacks_blocked": r["attacks_blocked"],
            "avg_risk": round(r["avg_risk"], 2),
        }
        for r in results
    ]

    return {"stats": stats, "period_days": days}
