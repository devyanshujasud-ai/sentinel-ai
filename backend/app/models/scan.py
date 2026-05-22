"""
Sentinel AI — Scan Model

MongoDB document structure for prompt scan records.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.utils.helpers import generate_id, utc_now


class ThreatMatch(BaseModel):
    """A single detected threat within a scanned prompt."""

    category: str
    severity: str  # LOW | MEDIUM | HIGH | CRITICAL
    confidence: float = Field(ge=0.0, le=1.0)
    matched_text: str
    explanation: str
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None


class ScanResult(BaseModel):
    """Full result of a prompt scan."""

    risk_score: float = Field(ge=0.0, le=100.0)
    overall_severity: str  # LOW | MEDIUM | HIGH | CRITICAL
    is_safe: bool
    threats_detected: int
    threat_matches: List[ThreatMatch] = []
    original_prompt: str
    sanitized_prompt: str
    target_llm: Optional[str] = None  # chatgpt | claude | gemini


class ScanModel(BaseModel):
    """Represents a scan document in the 'scans' collection."""

    id: str = Field(default_factory=generate_id, alias="_id")
    user_id: str
    prompt: str
    target_llm: Optional[str] = None
    result: ScanResult
    created_at: datetime = Field(default_factory=utc_now)

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        """Convert to MongoDB-insertable dict."""
        return self.model_dump(by_alias=True)

    def to_response(self) -> dict:
        """Convert to API response dict."""
        data = self.model_dump(by_alias=True)
        data["id"] = data.pop("_id")
        return data
