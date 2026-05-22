"""
Sentinel AI — Analytics Schemas

Response schemas for analytics endpoints.
"""

from typing import Dict, List
from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Dashboard summary statistics."""

    total_scans: int
    threats_detected: int
    attacks_blocked: int
    avg_risk_score: float
    safe_prompts: int
    unsafe_prompts: int


class TopThreat(BaseModel):
    """A single top threat entry."""

    category: str
    count: int
    percentage: float


class TopThreatsResponse(BaseModel):
    """Top threats response."""

    threats: List[TopThreat]
    total_threats: int


class RiskTrendPoint(BaseModel):
    """A single data point in risk trend."""

    date: str
    avg_risk_score: float
    total_scans: int
    threats_detected: int


class RiskTrendsResponse(BaseModel):
    """Risk trends over time."""

    trends: List[RiskTrendPoint]
    period_days: int


class DailyStatsPoint(BaseModel):
    """Daily statistics point."""

    date: str
    scans: int
    threats: int
    attacks_blocked: int
    avg_risk: float


class DailyStatsResponse(BaseModel):
    """Daily statistics response."""

    stats: List[DailyStatsPoint]
    period_days: int
