"""
Sentinel AI — Analytics Routes

Endpoints for dashboard stats, top threats, risk trends, and daily statistics.
"""

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_user
from app.services.analytics_service import (
    get_dashboard_stats,
    get_top_threats,
    get_risk_trends,
    get_daily_statistics,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def dashboard(current_user: dict = Depends(get_current_user)):
    """Get dashboard summary statistics."""
    stats = await get_dashboard_stats(current_user["id"])
    return {"status": "success", "data": stats}


@router.get("/top-threats")
async def top_threats(
    limit: int = Query(10, ge=1, le=50, description="Number of top threats"),
    current_user: dict = Depends(get_current_user),
):
    """Get top threat categories by frequency."""
    data = await get_top_threats(current_user["id"], limit)
    return {"status": "success", "data": data}


@router.get("/risk-trends")
async def risk_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    current_user: dict = Depends(get_current_user),
):
    """Get risk score trends over time."""
    data = await get_risk_trends(current_user["id"], days)
    return {"status": "success", "data": data}


@router.get("/daily-stats")
async def daily_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    current_user: dict = Depends(get_current_user),
):
    """Get daily scan and threat statistics."""
    data = await get_daily_statistics(current_user["id"], days)
    return {"status": "success", "data": data}
