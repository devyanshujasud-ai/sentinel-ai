"""
Sentinel AI — Base Detector

Abstract base class for all threat detectors in the pipeline.
"""

from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel, Field


class DetectorMatch(BaseModel):
    """Represents a single threat match found by a detector."""

    category: str
    severity: str  # LOW | MEDIUM | HIGH | CRITICAL
    confidence: float = Field(ge=0.0, le=1.0)
    matched_text: str
    explanation: str
    start_pos: int = -1
    end_pos: int = -1


class BaseDetector(ABC):
    """
    Abstract base class for all threat detectors.

    Each detector analyzes a prompt for a specific category of threat
    and returns a list of DetectorMatch objects.
    """

    name: str = "base_detector"
    category: str = "unknown"
    weight: float = 0.5  # Category weight for risk scoring (0.0 - 1.0)

    @abstractmethod
    async def detect(self, prompt: str) -> List[DetectorMatch]:
        """
        Analyze the given prompt for threats.

        Args:
            prompt: The raw prompt text to analyze.

        Returns:
            A list of DetectorMatch objects for any threats found.
        """
        ...
