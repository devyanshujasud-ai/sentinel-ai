"""
Sentinel AI — Analytics Model

MongoDB document structure for daily analytics snapshots.
"""

from datetime import datetime
from typing import Dict

from pydantic import BaseModel, Field

from app.utils.helpers import generate_id, utc_now


class DailyAnalytics(BaseModel):
    """Represents a daily analytics snapshot in the 'analytics' collection."""

    id: str = Field(default_factory=generate_id, alias="_id")
    user_id: str
    date: str  # YYYY-MM-DD format
    total_scans: int = 0
    threats_detected: int = 0
    attacks_blocked: int = 0
    avg_risk_score: float = 0.0
    max_risk_score: float = 0.0
    threat_categories: Dict[str, int] = {}  # category -> count
    severity_distribution: Dict[str, int] = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0,
    }
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        return self.model_dump(by_alias=True)

    def to_response(self) -> dict:
        data = self.model_dump(by_alias=True)
        data["id"] = data.pop("_id")
        return data
