"""
Sentinel AI — SQL Injection Detector

Detects SQL injection patterns that could be embedded in prompts
to trick LLMs into generating or executing malicious SQL.
"""

import re
from typing import List

from app.detection.base import BaseDetector, DetectorMatch


class SQLInjectionDetector(BaseDetector):
    """Detects SQL injection patterns in prompts."""

    name = "sql_injection"
    category = "SQL_INJECTION"
    weight = 0.85

    PATTERNS = [
        # Classic SQL injection
        (r"('\s*(OR|AND)\s*'?\s*\d+\s*=\s*\d+)", "CRITICAL", 0.95,
         "Classic SQL injection: tautology-based bypass"),
        (r"('\s*;\s*(DROP|DELETE|TRUNCATE|ALTER|UPDATE|INSERT)\s)", "CRITICAL", 0.95,
         "SQL injection with destructive command chaining"),
        (r"(UNION\s+(ALL\s+)?SELECT)", "HIGH", 0.90,
         "UNION-based SQL injection for data extraction"),
        (r"(DROP\s+(TABLE|DATABASE|INDEX|VIEW|SCHEMA))", "CRITICAL", 0.95,
         "Attempts to drop database objects"),
        (r"(DELETE\s+FROM\s+\w+)", "HIGH", 0.88,
         "Attempts to delete data from tables"),
        (r"(TRUNCATE\s+TABLE)", "HIGH", 0.90,
         "Attempts to truncate a table"),

        # Information extraction
        (r"(SELECT\s+.*\s+FROM\s+(information_schema|sys\.|mysql\.|pg_))", "HIGH", 0.88,
         "Attempts to extract database schema information"),
        (r"(LOAD_FILE|INTO\s+(OUT|DUMP)FILE)", "HIGH", 0.85,
         "File system access via SQL"),

        # Blind SQL injection
        (r"(SLEEP\s*\(\s*\d+\s*\)|BENCHMARK\s*\(|WAITFOR\s+DELAY)", "HIGH", 0.82,
         "Time-based blind SQL injection technique"),
        (r"(HAVING\s+\d+\s*=\s*\d+|GROUP\s+BY\s+.*\s+HAVING)", "MEDIUM", 0.75,
         "HAVING clause-based SQL injection"),

        # Comment-based bypass
        (r"(/\*.*?\*/|--\s+|#\s+.*$)", "MEDIUM", 0.60,
         "SQL comment syntax — possible filter bypass"),

        # Stored procedure exploitation
        (r"(EXEC(UTE)?\s+(xp_|sp_)|xp_cmdshell)", "CRITICAL", 0.93,
         "Attempts to execute system stored procedures"),
    ]

    KEYWORDS = [
        ("drop database", "CRITICAL", 0.95),
        ("drop table", "CRITICAL", 0.93),
        ("select * from", "MEDIUM", 0.65),
        ("union select", "HIGH", 0.88),
        ("or 1=1", "HIGH", 0.90),
        ("'; --", "HIGH", 0.85),
        ("information_schema", "HIGH", 0.82),
        ("xp_cmdshell", "CRITICAL", 0.95),
        ("insert into", "MEDIUM", 0.55),
        ("update set", "MEDIUM", 0.55),
    ]

    async def detect(self, prompt: str) -> List[DetectorMatch]:
        matches: List[DetectorMatch] = []
        prompt_lower = prompt.lower()

        for pattern, severity, confidence, explanation in self.PATTERNS:
            for match in re.finditer(pattern, prompt_lower, re.IGNORECASE):
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
                        explanation=f"Contains SQL injection keyword: '{keyword}'",
                        start_pos=idx,
                        end_pos=idx + len(keyword),
                    ))

        return matches
