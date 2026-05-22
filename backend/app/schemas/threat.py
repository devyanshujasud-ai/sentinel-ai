"""
Sentinel AI — Threat Schemas

Response schemas for threat definition endpoints.
"""

from typing import List
from pydantic import BaseModel


class ThreatResponse(BaseModel):
    """Schema for a single threat definition."""

    id: str
    category: str
    name: str
    description: str
    severity: str
    examples: List[str]
    weight: float
    is_active: bool


class ThreatListResponse(BaseModel):
    """Schema for threat list response."""

    threats: List[ThreatResponse]
    total: int
