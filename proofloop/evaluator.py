"""Pure validation and parsing helpers for ProofLoop."""

from __future__ import annotations

import json
import re
from typing import Any

VALID_VERDICTS = {"Aligned", "Partially aligned", "Not aligned", "Cannot determine"}
VALID_CONFIDENCE = {"High", "Medium", "Low"}


def validate_inputs(
    *,
    mode: str,
    guidelines: str,
    answer: str = "",
    output_a: str = "",
    output_b: str = "",
    comparison_feedback: str = "",
) -> list[str]:
    """Return user-facing validation errors; never inject demo/default content."""
    errors: list[str] = []
    if not guidelines.strip():
        errors.append("Paste the task guidelines before starting a review.")
    if mode == "comparison":
        if not output_a.strip():
            errors.append("Paste Output A for the comparison task.")
        if not output_b.strip():
            errors.append("Paste Output B for the comparison task.")
        if not comparison_feedback.strip():
            errors.append("Paste the annotator's comparison or feedback to review.")
    elif not answer.strip():
        errors.append("Paste the answer you want ProofLoop to check.")
    return errors


def _clean_json_text(text: str) -> str:
    cleaned = (text or "").strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    # Defensive fallback for models that add a short preface despite instructions.
    first = cleaned.find("{")
    last = cleaned.rfind("}")
    if first >= 0 and last > first:
        cleaned = cleaned[first : last + 1]
    return cleaned.strip()


def parse_review_response(raw: str) -> dict[str, Any]:
    """Parse and normalize model JSON. Preserve unparseable output for transparency."""
    try:
        data = json.loads(_clean_json_text(raw))
        if not isinstance(data, dict):
            raise ValueError("The response root is not a JSON object.")
    except (json.JSONDecodeError, ValueError, TypeError):
        return {
            "parse_ok": False,
            "verdict": "Review response needs inspection",
            "summary": "The model responded, but its result was not in the expected structured format. Review the raw response below rather than treating this as a completed verdict.",
            "issues": [],
            "strengths": [],
            "corrected_answer": "",
            "confidence": "Low",
            "limitations": "The model response could not be parsed into ProofLoop's expected format.",
            "raw_response": raw or "(Empty model response)",
        }

    verdict = str(data.get("verdict", "Cannot determine")).strip()
    if verdict not in VALID_VERDICTS:
        verdict = "Cannot determine"
    confidence = str(data.get("confidence", "Low")).strip()
    if confidence not in VALID_CONFIDENCE:
        confidence = "Low"

    issues = data.get("issues", [])
    strengths = data.get("strengths", [])
    if not isinstance(issues, list):
        issues = []
    if not isinstance(strengths, list):
        strengths = []
    issues = [item for item in issues if isinstance(item, dict)]
    strengths = [str(item).strip() for item in strengths if str(item).strip()]

    return {
        "parse_ok": True,
        "verdict": verdict,
        "summary": str(data.get("summary", "The model did not provide a summary." )).strip(),
        "issues": issues,
        "strengths": strengths,
        "corrected_answer": str(data.get("corrected_answer", "")).strip(),
        "confidence": confidence,
        "limitations": str(data.get("limitations", "")).strip(),
        "raw_response": raw or "(Empty model response)",
    }
