"""
Sentinel AI — Orchestrated Detection Engine

Aggregates rule-based token pattern matching with dynamic real-time
AI-powered moderation API sweeps. Includes smart confidence boosting,
intelligent severity classification, and parallelized explanation generation.
"""

import asyncio
import logging
from typing import List, Dict, Any

from app.detection.base import BaseDetector, DetectorMatch
from app.detection.prompt_injection import PromptInjectionDetector
from app.detection.jailbreak import JailbreakDetector
from app.detection.sql_injection import SQLInjectionDetector
from app.detection.shell_command import ShellCommandDetector
from app.detection.toxicity import ToxicityDetector
from app.detection.data_leakage import DataLeakageDetector
from app.detection.code_safety import CodeSafetyDetector
from app.detection.role_manipulation import RoleManipulationDetector
from app.detection.sanitizer import PromptSanitizer
from app.detection.ai_moderator import get_ai_moderator, AIModerationVerdict
from app.utils.helpers import clamp, severity_from_score, SEVERITY_MULTIPLIER

logger = logging.getLogger("sentinel.detection")

# Category weights for risk score calculation
CATEGORY_WEIGHTS = {
    "PROMPT_INJECTION": 0.95,
    "JAILBREAK": 0.95,
    "SQL_INJECTION": 0.85,
    "SHELL_COMMAND": 0.90,
    "TOXICITY": 0.75,
    "DATA_LEAKAGE": 0.85,
    "UNSAFE_CODE": 0.80,
    "ROLE_MANIPULATION": 0.85,
}


class DetectionEngine:
    """
    Core hybrid detection pipeline.
    Combines rule-based matching with AI moderation in parallel.
    """

    def __init__(self):
        self.detectors: List[BaseDetector] = [
            PromptInjectionDetector(),
            JailbreakDetector(),
            SQLInjectionDetector(),
            ShellCommandDetector(),
            ToxicityDetector(),
            DataLeakageDetector(),
            CodeSafetyDetector(),
            RoleManipulationDetector(),
        ]
        self.sanitizer = PromptSanitizer()
        self.ai_moderator = get_ai_moderator()

    async def analyze(self, prompt: str) -> dict:
        """
        Runs rules + AI moderation concurrently and computes advanced metrics.
        """
        # Run all detectors and AI moderation concurrently
        tasks = [detector.detect(prompt) for detector in self.detectors]
        tasks.append(self.ai_moderator.moderate(prompt))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_matches: List[DetectorMatch] = []
        ai_verdict: Optional[AIModerationVerdict] = None

        # Process results
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                logger.error(f"Engine component failed: {res}")
                continue

            if i < len(self.detectors):
                # Rule-based detector match list
                all_matches.extend(res)
            else:
                # AI Moderation Verdict
                ai_verdict = res

        # 1. Combine Rule-based + AI Moderation
        if ai_verdict and not ai_verdict.is_safe:
            # Check if we already have a rule-based match for this category
            matched_categories = {m.category for m in all_matches}
            if ai_verdict.category not in matched_categories:
                # Add AI moderation match as a new high-quality match
                all_matches.append(
                    DetectorMatch(
                        category=ai_verdict.category or "TOXICITY",
                        matched_text=prompt[:60] + "...",
                        confidence=ai_verdict.confidence,
                        severity="HIGH",
                        explanation=ai_verdict.explanation or "Flagged by AI-powered moderator."
                    )
                )

        # 2. Multi-Signal Consensus & Confidence Boosting
        # Boost confidence if both AI Moderation and rules flag the same category
        if ai_verdict and not ai_verdict.is_safe:
            for match in all_matches:
                if match.category == ai_verdict.category:
                    # Boost confidence using geometric consensus formula
                    old_conf = match.confidence
                    boosted = old_conf + (1.0 - old_conf) * 0.5
                    match.confidence = round(clamp(boosted, 0.0, 1.0), 3)
                    logger.debug(f"Boosted category {match.category} confidence from {old_conf} to {match.confidence} via AI consensus.")

        # 3. Intelligent Severity & Risk Score Calculation
        risk_score = self._calculate_risk_score(all_matches)
        overall_severity = severity_from_score(risk_score)
        is_safe = len(all_matches) == 0

        # Adjust individual match severities based on confidence threshold and weights
        for match in all_matches:
            weight = CATEGORY_WEIGHTS.get(match.category, 0.5)
            # If weight is high and confidence > 0.85, elevate to CRITICAL
            if weight >= 0.90 and match.confidence >= 0.85:
                match.severity = "CRITICAL"
            elif match.confidence >= 0.60:
                match.severity = "HIGH"
            elif match.confidence >= 0.35:
                match.severity = "MEDIUM"
            else:
                match.severity = "LOW"

        # 4. Asynchronous Explanation Generation
        # Generate custom AI explanations for active threat matches concurrently
        explanation_tasks = []
        for match in all_matches:
            explanation_tasks.append(
                self.ai_moderator.generate_explanation(
                    prompt=prompt,
                    category=match.category,
                    matched_text=match.matched_text
                )
            )

        explanations = await asyncio.gather(*explanation_tasks, return_exceptions=True)

        for idx, match in enumerate(all_matches):
            if idx < len(explanations) and not isinstance(explanations[idx], Exception):
                match.explanation = explanations[idx]

        # 5. Sanitization
        sanitized_prompt = self.sanitizer.sanitize(prompt, all_matches)

        # Build clean Pydantic-compatible JSON match array
        threat_match_dicts = [
            {
                "category": m.category,
                "severity": m.severity,
                "confidence": round(m.confidence, 3),
                "matched_text": m.matched_text,
                "explanation": m.explanation,
            }
            for m in all_matches
        ]

        return {
            "risk_score": round(risk_score, 2),
            "overall_severity": overall_severity,
            "is_safe": is_safe,
            "threats_detected": len(all_matches),
            "threat_matches": threat_match_dicts,
            "original_prompt": prompt,
            "sanitized_prompt": sanitized_prompt,
        }

    def _calculate_risk_score(self, matches: List[DetectorMatch]) -> float:
        """
        Calculate overall risk score from detected threats.
        Formula: min(100, sum(weight * confidence * severity_multiplier) * 10)
        """
        if not matches:
            return 0.0

        total = 0.0
        for match in matches:
            weight = CATEGORY_WEIGHTS.get(match.category, 0.5)
            severity_mult = SEVERITY_MULTIPLIER.get(match.severity, 1.0)
            total += weight * match.confidence * severity_mult

        score = total * 10
        return clamp(score, 0.0, 100.0)
