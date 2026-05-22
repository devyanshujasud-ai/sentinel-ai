"""
Sentinel AI — Threat Model

MongoDB document structure for threat definitions.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.utils.helpers import generate_id, utc_now


class ThreatDefinition(BaseModel):
    """Represents a threat definition in the 'threats' collection."""

    id: str = Field(default_factory=generate_id, alias="_id")
    category: str
    name: str
    description: str
    severity: str  # LOW | MEDIUM | HIGH | CRITICAL
    examples: List[str] = []
    detection_patterns: List[str] = []
    weight: float = Field(default=0.5, ge=0.0, le=1.0)
    is_active: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        return self.model_dump(by_alias=True)

    def to_response(self) -> dict:
        data = self.model_dump(by_alias=True)
        data["id"] = data.pop("_id")
        return data
