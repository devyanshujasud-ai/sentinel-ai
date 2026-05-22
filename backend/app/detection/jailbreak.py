"""
Sentinel AI — Jailbreak Detector

Detects attempts to bypass LLM safety guidelines, including DAN-style
prompts, role-playing exploits, and constraint removal techniques.
"""

import re
from typing import List

from app.detection.base import BaseDetector, DetectorMatch


class JailbreakDetector(BaseDetector):
    """Detects jailbreak and safety bypass attempts."""

    name = "jailbreak"
    category = "JAILBREAK"
    weight = 0.95

    PATTERNS = [
        # DAN-style jailbreaks
        (r"\bDAN\b", "CRITICAL", 0.90,
         "References DAN (Do Anything Now) jailbreak technique"),
        (r"do\s+anything\s+now", "CRITICAL", 0.92,
         "Classic DAN jailbreak phrase"),
        (r"(developer|debug|maintenance|god)\s+mode", "CRITICAL", 0.90,
         "Attempts to activate privileged mode"),

        # Role-playing exploits
        (r"(act|behave|respond|pretend|roleplay)\s+(as\s+)?(an?\s+)?(unrestricted|unfiltered|uncensored|evil|malicious)", "HIGH", 0.88,
         "Attempts to make model act without restrictions"),
        (r"you\s+are\s+(now\s+)?(free|liberated|unrestricted|unchained|unshackled)", "HIGH", 0.85,
         "Attempts to 'free' the model from safety guidelines"),
        (r"(remove|disable|bypass|ignore|override)\s+(all\s+)?(your\s+)?(safety|content|ethical)\s*(filters?|guidelines?|restrictions?|guardrails?)", "CRITICAL", 0.93,
         "Directly attempts to disable safety filters"),

        # Constraint removal
        (r"(no|without)\s+(rules?|restrictions?|limitations?|boundaries?|constraints?|guidelines?)", "HIGH", 0.82,
         "Requests operation without safety constraints"),
        (r"(can|will|should)\s+say\s+anything", "MEDIUM", 0.70,
         "Encourages unrestricted output"),
        (r"nothing\s+is\s+(off[\s-]limits?|forbidden|restricted)", "HIGH", 0.80,
         "Claims no content is restricted"),

        # Token manipulation
        (r"respond\s+with\s+(only\s+)?(yes|sure|ok|affirmative)\s+(regardless|no\s+matter|always)", "HIGH", 0.78,
         "Attempts to force affirmative-only responses"),
        (r"(hypothetical|theoretical|fictional)\s+(scenario|situation|world)\s+where\s+(you\s+)?(have\s+no|don't\s+have|lack)\s+(rules?|restrictions?)", "HIGH", 0.80,
         "Uses hypothetical framing to bypass restrictions"),

        # Prompt leaking / splitting
        (r"(split|divide|separate)\s+(your\s+)?(response|answer|output)\s+into\s+(two|2|multiple)\s+(parts?|sections?)", "MEDIUM", 0.65,
         "Possible prompt splitting technique"),

        # Known jailbreak names
        (r"\b(STAN|DUDE|AIM|KEVIN|MONGO|ANTI[\s-]?GPT)\b", "HIGH", 0.85,
         "References a known jailbreak persona"),
    ]

    KEYWORDS = [
        ("jailbreak", "CRITICAL", 0.92),
        ("bypass safety", "CRITICAL", 0.90),
        ("bypass content filter", "CRITICAL", 0.90),
        ("act without restrictions", "HIGH", 0.85),
        ("pretend you are evil", "HIGH", 0.82),
        ("unfiltered mode", "HIGH", 0.85),
        ("no ethical guidelines", "HIGH", 0.83),
        ("ignore your training", "HIGH", 0.88),
        ("override your programming", "HIGH", 0.87),
        ("break character", "MEDIUM", 0.60),
        ("enable developer mode", "CRITICAL", 0.90),
    ]

    async def detect(self, prompt: str) -> List[DetectorMatch]:
        matches: List[DetectorMatch] = []
        prompt_lower = prompt.lower()

        for pattern, severity, confidence, explanation in self.PATTERNS:
            for match in re.finditer(pattern, prompt_lower):
                matches.append(DetectorMatch(
                    category=self.category,
                    severity=severity,
                    confidence=confidence,
                    matched_text=prompt[match.start():match.end()],
                    explanation=explanation,
                    start_pos=match.start(),
                    end_pos=match.end(),
                ))

        for keyword, severity, confidence in self.KEYWORDS:
            idx = prompt_lower.find(keyword)
            if idx != -1:
                if not any(m.start_pos <= idx < m.end_pos for m in matches):
                    matches.append(DetectorMatch(
                        category=self.category,
                        severity=severity,
                        confidence=confidence,
                        matched_text=prompt[idx:idx + len(keyword)],
                        explanation=f"Contains jailbreak keyword: '{keyword}'",
                        start_pos=idx,
                        end_pos=idx + len(keyword),
                    ))

        return matches
