"""
Sentinel AI — Prompt Sanitizer

Replaces detected threat content with safe placeholders.
"""

from typing import List
from app.detection.base import DetectorMatch

PLACEHOLDER = "[SUSPICIOUS CONTENT REMOVED]"


class PromptSanitizer:
    """Sanitizes prompts by replacing detected threat matches with placeholders."""

    @staticmethod
    def sanitize(prompt: str, matches: List[DetectorMatch]) -> str:
        """
        Replace all detected threat regions in the prompt with a safe placeholder.

        Handles overlapping matches by merging ranges before replacement.

        Args:
            prompt: The original prompt text.
            matches: List of DetectorMatch objects with start/end positions.

        Returns:
            Sanitized prompt string.
        """
        if not matches:
            return prompt

        # Collect valid ranges (with positions)
        ranges = [
            (m.start_pos, m.end_pos)
            for m in matches
            if m.start_pos >= 0 and m.end_pos > m.start_pos
        ]

        if not ranges:
            return prompt

        # Sort by start position
        ranges.sort(key=lambda r: r[0])

        # Merge overlapping ranges
        merged: list[tuple[int, int]] = [ranges[0]]
        for start, end in ranges[1:]:
            prev_start, prev_end = merged[-1]
            if start <= prev_end:
                merged[-1] = (prev_start, max(prev_end, end))
            else:
                merged.append((start, end))

        # Build sanitized string by replacing matched regions
        result_parts: list[str] = []
        last_end = 0

        for start, end in merged:
            result_parts.append(prompt[last_end:start])
            result_parts.append(PLACEHOLDER)
            last_end = end

        result_parts.append(prompt[last_end:])
        return "".join(result_parts)
