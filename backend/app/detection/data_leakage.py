"""
Sentinel AI — Data Leakage Detector

Detects sensitive data patterns: SSNs, credit cards, API keys, emails, phone numbers.
"""

import re
from typing import List
from app.detection.base import BaseDetector, DetectorMatch


class DataLeakageDetector(BaseDetector):
    name = "data_leakage"
    category = "DATA_LEAKAGE"
    weight = 0.85

    PATTERNS = [
        (r"\b\d{3}-\d{2}-\d{4}\b", "CRITICAL", 0.92, "Social Security Number (SSN) pattern detected"),
        (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "CRITICAL", 0.90, "Credit card number pattern detected"),
        (r"\b[A-Za-z0-9]{20,40}\b(?=.*(api[_\s-]?key|secret[_\s-]?key|access[_\s-]?token|private[_\s-]?key))", "HIGH", 0.80,
         "Potential API key or secret token detected"),
        (r"(sk|pk|api|key|token|secret|password|credential)[-_]?[a-zA-Z0-9]{16,}", "HIGH", 0.78,
         "Possible API key or secret credential"),
        (r"(my\s+)?(ssn|social\s+security)\s+(is|number|:)\s*\d", "CRITICAL", 0.93,
         "User sharing Social Security Number"),
        (r"(my\s+)?(credit\s+card|card\s+number|debit\s+card)\s+(is|number|:)\s*\d", "CRITICAL", 0.93,
         "User sharing credit card information"),
        (r"(my\s+)?(password|passwd|secret)\s+(is|:)\s*\S+", "HIGH", 0.85,
         "User sharing password or secret"),
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "MEDIUM", 0.55,
         "Email address detected"),
        (r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", "LOW", 0.45,
         "Phone number pattern detected"),
        (r"(AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}", "CRITICAL", 0.95,
         "AWS Access Key ID detected"),
        (r"ghp_[A-Za-z0-9]{36}", "CRITICAL", 0.95, "GitHub Personal Access Token detected"),
    ]

    KEYWORDS = [
        ("my social security number", "CRITICAL", 0.90),
        ("my credit card number", "CRITICAL", 0.90),
        ("my password is", "HIGH", 0.85),
        ("my api key is", "HIGH", 0.82),
        ("my bank account", "HIGH", 0.75),
        ("my private key", "HIGH", 0.82),
    ]

    async def detect(self, prompt: str) -> List[DetectorMatch]:
        matches: List[DetectorMatch] = []
        prompt_lower = prompt.lower()

        for pattern, severity, confidence, explanation in self.PATTERNS:
            for match in re.finditer(pattern, prompt, re.IGNORECASE):
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
                    explanation=f"Sensitive data disclosure: '{keyword}'",
                    start_pos=idx, end_pos=idx + len(keyword),
                ))
        return matches
