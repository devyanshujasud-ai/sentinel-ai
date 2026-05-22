"""
Sentinel AI — Role Manipulation Detector

Detects attempts to manipulate the LLM's assigned role or extract system instructions.
"""

import re
from typing import List
from app.detection.base import BaseDetector, DetectorMatch


class RoleManipulationDetector(BaseDetector):
    name = "role_manipulation"
    category = "ROLE_MANIPULATION"
    weight = 0.85

    PATTERNS = [
        (r"(reveal|show|display|print|tell\s+me)\s+(your\s+)?(system\s+prompt|system\s+message|initial\s+prompt|hidden\s+instructions?)", "HIGH", 0.90,
         "Attempts to extract system prompt"),
        (r"what\s+(are|were)\s+your\s+(instructions?|rules?|guidelines?|system\s+prompt)", "HIGH", 0.85,
         "Asks about model instructions"),
        (r"(act|pretend|behave)\s+(as|like)\s+(root|admin|administrator|superuser|system)", "HIGH", 0.85,
         "Attempts to assume privileged role"),
        (r"you\s+are\s+(now\s+)?(a|an|my)\s+(hacker|criminal|evil|malicious)", "HIGH", 0.82,
         "Assigns malicious role to model"),
        (r"(switch|change)\s+(to|your)\s+(role|persona|character|identity)", "MEDIUM", 0.70,
         "Attempts to switch model's role"),
        (r"(forget|abandon|drop)\s+(your\s+)?(current\s+)?(role|persona|character|identity)", "HIGH", 0.80,
         "Attempts to make model abandon its role"),
        (r"(repeat|echo|recite)\s+(everything|all|your)\s+(above|before|previous|system)", "HIGH", 0.82,
         "Attempts to extract prior context"),
        (r"what\s+(is|was)\s+(the\s+)?(first|original|initial)\s+(thing|message|prompt)\s+(said|given|sent)", "HIGH", 0.80,
         "Attempts to extract initial prompt"),
    ]

    KEYWORDS = [
        ("reveal system prompt", "HIGH", 0.90),
        ("what are your instructions", "HIGH", 0.82),
        ("act as root", "HIGH", 0.82),
        ("act as admin", "HIGH", 0.80),
        ("pretend to be a hacker", "HIGH", 0.80),
        ("show me your prompt", "HIGH", 0.85),
        ("print your system message", "HIGH", 0.88),
        ("ignore your role", "HIGH", 0.82),
    ]

    async def detect(self, prompt: str) -> List[DetectorMatch]:
        matches: List[DetectorMatch] = []
        prompt_lower = prompt.lower()

        for pattern, severity, confidence, explanation in self.PATTERNS:
            for match in re.finditer(pattern, prompt_lower):
                matches.append(DetectorMatch(
                    category=self.category, severity=severity, confidence=confidence,
                    matched_text=prompt[match.start():match.end()],
                    explanation=explanation, start_pos=match.start(), end_pos=match.end(),
                ))

        for keyword, severity, confidence in self.KEYWORDS:
            idx = prompt_lower.find(keyword)
            if idx != -1 and not any(m.start_pos <= idx < m.end_pos for m in matches):
                matches.append(DetectorMatch(
                    category=self.category, severity=severity, confidence=confidence,
                    matched_text=prompt[idx:idx + len(keyword)],
                    explanation=f"Role manipulation attempt: '{keyword}'",
                    start_pos=idx, end_pos=idx + len(keyword),
                ))
        return matches
