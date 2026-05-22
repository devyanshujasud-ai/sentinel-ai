"""
Sentinel AI — Toxicity Detector

Detects toxic, hateful, violent, or abusive content in prompts.
"""

import re
from typing import List
from app.detection.base import BaseDetector, DetectorMatch


class ToxicityDetector(BaseDetector):
    name = "toxicity"
    category = "TOXICITY"
    weight = 0.75

    PATTERNS = [
        (r"(how\s+to\s+)?(make|build|create)\s+(a\s+)?(bomb|explosive|weapon|poison)", "CRITICAL", 0.93,
         "Requests creation of weapons or dangerous materials"),
        (r"(kill|murder|assassinate|harm)\s+(someone|a\s+person|people)", "CRITICAL", 0.95,
         "Contains violence against persons"),
        (r"(how\s+to\s+)(poison|kidnap|stalk|harass)\s+(someone|a\s+person)", "CRITICAL", 0.93,
         "Requests methods to harm others"),
        (r"(how\s+to\s+)(commit\s+suicide|kill\s+myself|end\s+my\s+life)", "CRITICAL", 0.95,
         "Self-harm content"),
        (r"(write|generate|create)\s+(a\s+)?(threat|hate\s+mail|death\s+threat)", "HIGH", 0.88,
         "Requests generation of threatening content"),
        (r"(hack\s+into|break\s+into|steal\s+from)", "HIGH", 0.80,
         "Requests criminal activities"),
    ]

    SIGNAL_WORDS = [
        ("kill them all", "HIGH", 0.85),
        ("death threat", "HIGH", 0.85),
        ("make a bomb", "CRITICAL", 0.90),
        ("build a weapon", "CRITICAL", 0.88),
        ("generate hate speech", "HIGH", 0.88),
        ("create malware", "HIGH", 0.82),
        ("generate ransomware", "CRITICAL", 0.90),
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

        for keyword, severity, confidence in self.SIGNAL_WORDS:
            idx = prompt_lower.find(keyword)
            if idx != -1 and not any(m.start_pos <= idx < m.end_pos for m in matches):
                matches.append(DetectorMatch(
                    category=self.category, severity=severity, confidence=confidence,
                    matched_text=prompt[idx:idx + len(keyword)],
                    explanation=f"Contains toxic content: '{keyword}'",
                    start_pos=idx, end_pos=idx + len(keyword),
                ))
        return matches
