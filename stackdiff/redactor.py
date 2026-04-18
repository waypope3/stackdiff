"""Redact sensitive values from stack outputs before display or export."""

from __future__ import annotations

import re
from typing import Dict, List

from stackdiff.differ import KeyDiff

_DEFAULT_PATTERNS: List[str] = [
    r"(?i)password",
    r"(?i)secret",
    r"(?i)token",
    r"(?i)api.?key",
    r"(?i)private.?key",
]

REDACTED = "***REDACTED***"


def _matches_any(key: str, patterns: List[str]) -> bool:
    return any(re.search(p, key) for p in patterns)


def redact_value(key: str, value: str, patterns: List[str]) -> str:
    """Return REDACTED if key matches any sensitive pattern, else value."""
    if not isinstance(value, str):
        raise TypeError(f"value must be str, got {type(value).__name__}")
    return REDACTED if _matches_any(key, patterns) else value


def redact_stack(outputs: Dict[str, str], patterns: List[str] | None = None) -> Dict[str, str]:
    """Return a copy of outputs with sensitive values redacted."""
    pats = patterns if patterns is not None else _DEFAULT_PATTERNS
    return {k: redact_value(k, v, pats) for k, v in outputs.items()}


def redact_diffs(diffs: List[KeyDiff], patterns: List[str] | None = None) -> List[KeyDiff]:
    """Return new KeyDiff list with sensitive baseline/target values redacted."""
    pats = patterns if patterns is not None else _DEFAULT_PATTERNS
    result: List[KeyDiff] = []
    for d in diffs:
        if _matches_any(d.key, pats):
            result.append(KeyDiff(
                key=d.key,
                baseline=REDACTED if d.baseline is not None else None,
                target=REDACTED if d.target is not None else None,
                changed=d.changed,
            ))
        else:
            result.append(d)
    return result
