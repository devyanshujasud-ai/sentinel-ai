"""
Sentinel AI — Scan Schemas

Request and response schemas for prompt scanning endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    """Schema for submitting a prompt for scanning."""

    prompt: str = Field(min_length=1, max_length=50000, description="The prompt text to scan.")
    target_llm: Optional[str] = Field(
        default=None,
        description="Target LLM: chatgpt, claude, gemini",
        pattern="^(chatgpt|claude|gemini)$",
    )


class ThreatMatchResponse(BaseModel):
    """Schema for a single threat match in scan results."""

    category: str
    severity: str
    confidence: float
    matched_text: str
    explanation: str


class ScanResponse(BaseModel):
    """Schema for scan result response."""

    id: str
    risk_score: float
    overall_severity: str
    is_safe: bool
    threats_detected: int
    threat_matches: List[ThreatMatchResponse]
    original_prompt: str
    sanitized_prompt: str
    target_llm: Optional[str] = None
    created_at: str


class ScanHistoryResponse(BaseModel):
    """Schema for paginated scan history."""

    scans: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int
