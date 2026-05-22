"""
Sentinel AI — Shell Command Detector

Detects dangerous shell/system commands embedded in prompts that could
be used to trick LLMs into generating destructive operations.
"""

import re
from typing import List

from app.detection.base import BaseDetector, DetectorMatch


class ShellCommandDetector(BaseDetector):
    """Detects dangerous shell commands in prompts."""

    name = "shell_command"
    category = "SHELL_COMMAND"
    weight = 0.90

    PATTERNS = [
        # Destructive file operations
        (r"(sudo\s+)?rm\s+(-\w+\s+)*(/|~|\*)", "CRITICAL", 0.95,
         "Destructive file removal command (rm with dangerous paths)"),
        (r"(sudo\s+)?rm\s+-rf\b", "CRITICAL", 0.95,
         "Recursive force deletion command"),
        (r"(sudo\s+)?mkfs\b", "CRITICAL", 0.93,
         "Filesystem formatting command — will destroy data"),
        (r"(sudo\s+)?dd\s+if=.*of=/dev/", "CRITICAL", 0.93,
         "Low-level disk write command — can destroy drives"),

        # Privilege escalation
        (r"(sudo\s+)?(chmod\s+777|chmod\s+-R\s+777)", "HIGH", 0.85,
         "Sets world-writable permissions — security risk"),
        (r"(sudo\s+)?(chown\s+root|chgrp\s+root)", "HIGH", 0.80,
         "Changes ownership to root"),
        (r"(sudo\s+)?passwd\s+root", "HIGH", 0.85,
         "Attempts to change root password"),

        # Remote code execution
        (r"(curl|wget)\s+.*\|\s*(ba)?sh", "CRITICAL", 0.92,
         "Downloads and executes remote script — RCE risk"),
        (r"(curl|wget)\s+-[a-zA-Z]*O?\s+https?://", "MEDIUM", 0.60,
         "Downloads file from remote URL"),
        (r"(nc|ncat|netcat)\s+-[a-zA-Z]*\s+", "HIGH", 0.80,
         "Netcat command — potential reverse shell"),
        (r"bash\s+-i\s+>&\s*/dev/tcp/", "CRITICAL", 0.95,
         "Reverse shell command"),

        # System manipulation
        (r"(sudo\s+)?(shutdown|reboot|halt|poweroff|init\s+[06])", "HIGH", 0.85,
         "System shutdown or reboot command"),
        (r"(sudo\s+)?(iptables|ufw)\s+.*(ACCEPT|DROP|REJECT)", "HIGH", 0.78,
         "Firewall rule modification"),
        (r"(crontab\s+-[er]|/etc/cron)", "MEDIUM", 0.65,
         "Cron job manipulation"),
        (r"echo\s+.*>\s*/etc/(passwd|shadow|hosts|sudoers)", "CRITICAL", 0.93,
         "Writes to critical system files"),

        # Fork bombs and resource exhaustion
        (r":\(\)\s*\{\s*:\|\s*:\s*&\s*\}\s*;?\s*:", "CRITICAL", 0.95,
         "Fork bomb — will crash the system"),
        (r"while\s+true\s*;\s*do", "MEDIUM", 0.55,
         "Infinite loop — potential denial of service"),
    ]

    KEYWORDS = [
        ("sudo rm -rf", "CRITICAL", 0.95),
        ("rm -rf /", "CRITICAL", 0.97),
        ("chmod 777", "HIGH", 0.82),
        ("curl | bash", "CRITICAL", 0.90),
        ("wget | sh", "CRITICAL", 0.90),
        ("reverse shell", "CRITICAL", 0.92),
        ("fork bomb", "CRITICAL", 0.93),
        ("format c:", "CRITICAL", 0.90),
        ("del /f /s /q", "HIGH", 0.85),
        ("shutdown -s", "HIGH", 0.80),
        ("mkfs.ext4", "CRITICAL", 0.90),
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
                        explanation=f"Contains dangerous shell command: '{keyword}'",
                        start_pos=idx,
                        end_pos=idx + len(keyword),
                    ))

        return matches
