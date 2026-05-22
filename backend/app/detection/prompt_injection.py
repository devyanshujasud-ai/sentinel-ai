"""
Sentinel AI — Prompt Injection Detector

Detects attempts to override, ignore, or manipulate the system prompt
or previous instructions given to an LLM.
"""

import re
from typing import List

from app.detection.base import BaseDetector, DetectorMatch


class PromptInjectionDetector(BaseDetector):
    """Detects prompt injection attacks."""

    name = "prompt_injection"
    category = "PROMPT_INJECTION"
    weight = 0.95

    PATTERNS = [
        # Direct instruction override
        (r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?|context)", "CRITICAL", 0.95,
         "Attempts to override previous instructions"),
        (r"disregard\s+(all\s+)?(previous|prior|above|earlier|your)\s+(instructions?|prompts?|rules?|guidelines?)", "CRITICAL", 0.95,
         "Attempts to disregard system instructions"),
        (r"forget\s+(everything|all|your)\s+(you\s+)?(know|were told|instructions?)", "CRITICAL", 0.90,
         "Attempts to make the model forget its instructions"),

        # New instruction injection
        (r"(new|updated|revised|real)\s+instructions?\s*:", "HIGH", 0.85,
         "Injects new instructions into the prompt"),
        (r"your\s+(actual|real|true|new)\s+(purpose|role|instructions?|task)", "HIGH", 0.85,
         "Attempts to redefine the model's purpose"),
        (r"from\s+now\s+on\s*,?\s*(you\s+)?(are|will|should|must)", "HIGH", 0.80,
         "Attempts to alter model behavior going forward"),

        # System prompt extraction
        (r"(reveal|show|display|print|output|repeat)\s+(your\s+)?(system\s+prompt|initial\s+instructions?|hidden\s+prompt)", "HIGH", 0.90,
         "Attempts to extract the system prompt"),
        (r"what\s+(are|were)\s+your\s+(original|initial|system|first)\s+(instructions?|prompt|rules?)", "HIGH", 0.85,
         "Attempts to extract original instructions"),

        # Delimiter attacks
        (r"---+\s*(system|admin|root|developer|internal)\s*(message|prompt|instructions?|override)\s*---+", "CRITICAL", 0.92,
         "Uses delimiters to simulate system-level messages"),
        (r"\[SYSTEM\]|\[ADMIN\]|\[INTERNAL\]|\[OVERRIDE\]", "HIGH", 0.88,
         "Uses bracket tags to simulate system messages"),

        # Encoded / obfuscated injection
        (r"b(a|4)s(e|3)6(4|f)\s*(decode|encoded?)", "MEDIUM", 0.70,
         "Possible attempt to use encoded payloads to bypass filters"),
    ]

    KEYWORDS = [
        ("ignore previous instructions", "CRITICAL", 0.95),
        ("disregard your instructions", "CRITICAL", 0.95),
        ("override system prompt", "CRITICAL", 0.93),
        ("new system prompt", "HIGH", 0.88),
        ("you are now", "MEDIUM", 0.60),
        ("act as if you have no restrictions", "HIGH", 0.85),
        ("pretend your instructions", "HIGH", 0.80),
        ("do not follow your", "HIGH", 0.82),
    ]

    async def detect(self, prompt: str) -> List[DetectorMatch]:
        matches: List[DetectorMatch] = []
        prompt_lower = prompt.lower()

        # Regex pattern matching
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

        # Keyword matching
        for keyword, severity, confidence in self.KEYWORDS:
            idx = prompt_lower.find(keyword)
            if idx != -1:
                # Avoid duplicates from regex matches
                if not any(m.start_pos <= idx < m.end_pos for m in matches):
                    matches.append(DetectorMatch(
                        category=self.category,
                        severity=severity,
                        confidence=confidence,
                        matched_text=prompt[idx:idx + len(keyword)],
                        explanation=f"Contains prompt injection keyword: '{keyword}'",
                        start_pos=idx,
                        end_pos=idx + len(keyword),
                    ))

        return matches
