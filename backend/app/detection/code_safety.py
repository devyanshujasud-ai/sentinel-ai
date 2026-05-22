"""
Sentinel AI — Unsafe Code Generation Detector

Detects prompts requesting generation of dangerous code patterns.
"""

import re
from typing import List
from app.detection.base import BaseDetector, DetectorMatch


class CodeSafetyDetector(BaseDetector):
    name = "code_safety"
    category = "UNSAFE_CODE"
    weight = 0.80

    PATTERNS = [
        (r"\beval\s*\(", "HIGH", 0.82, "Use of eval() — arbitrary code execution risk"),
        (r"\bexec\s*\(", "HIGH", 0.82, "Use of exec() — arbitrary code execution risk"),
        (r"\bos\.system\s*\(", "HIGH", 0.85, "Use of os.system() — shell command execution"),
        (r"\bsubprocess\.(call|run|Popen)\s*\(", "HIGH", 0.80, "Subprocess execution"),
        (r"\b__import__\s*\(", "HIGH", 0.82, "Dynamic import — potential code injection"),
        (r"\bcompile\s*\(.*exec", "HIGH", 0.78, "Dynamic code compilation and execution"),
        (r"(pickle\.loads?|yaml\.load\s*\((?!.*Loader))", "HIGH", 0.80,
         "Insecure deserialization — arbitrary code execution risk"),
        (r"(ctypes|cffi|mmap)\.", "MEDIUM", 0.60, "Low-level memory access"),
        (r"\bsocket\.(socket|connect|bind|listen)", "MEDIUM", 0.55, "Network socket operations"),
        (r"(write|generate|create)\s+(a\s+)?(virus|trojan|worm|rootkit|keylogger|spyware|backdoor)", "CRITICAL", 0.93,
         "Requests creation of malicious software"),
        (r"(write|generate|create)\s+(a\s+)?(exploit|payload|shellcode|buffer\s+overflow)", "CRITICAL", 0.90,
         "Requests creation of exploit code"),
        (r"(write|generate)\s+(a\s+)?(sql\s+injection|xss|csrf)\s+(script|code|payload)", "HIGH", 0.85,
         "Requests generation of attack code"),
    ]

    KEYWORDS = [
        ("write a virus", "CRITICAL", 0.92),
        ("create a trojan", "CRITICAL", 0.92),
        ("generate malware", "CRITICAL", 0.92),
        ("write a keylogger", "CRITICAL", 0.90),
        ("create a backdoor", "CRITICAL", 0.90),
        ("write exploit code", "HIGH", 0.85),
        ("buffer overflow exploit", "HIGH", 0.85),
        ("reverse engineering", "MEDIUM", 0.50),
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
                    explanation=f"Unsafe code request: '{keyword}'",
                    start_pos=idx, end_pos=idx + len(keyword),
                ))
        return matches
