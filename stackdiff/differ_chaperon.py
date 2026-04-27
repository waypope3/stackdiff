"""differ_chaperon: pair each diff with a related 'companion' key from the same stack.

A companion is the other key whose value most closely resembles the current
key's baseline value, giving analysts a quick cross-reference when a value
changes (e.g. an ARN is replaced by another ARN that already exists).
"""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class ChaperondDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    companion_key: Optional[str] = None
    companion_similarity: float = 0.0

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "companion_key": self.companion_key,
            "companion_similarity": round(self.companion_similarity, 4),
        }

    def __str__(self) -> str:
        marker = "~" if self.changed else "="
        companion = f" (companion: {self.companion_key})" if self.companion_key else ""
        return f"[{marker}] {self.key}{companion}"


def _similarity(a: Optional[str], b: Optional[str]) -> float:
    """Normalised character overlap between two strings (0.0 – 1.0)."""
    if not a or not b:
        return 0.0
    common = sum(ca == cb for ca, cb in zip(a, b))
    return common / max(len(a), len(b))


def _find_companion(
    key: str,
    baseline_value: Optional[str],
    all_diffs: Sequence[KeyDiff],
    min_similarity: float,
    exclude_patterns: Sequence[str],
) -> tuple[Optional[str], float]:
    best_key: Optional[str] = None
    best_score: float = 0.0
    for other in all_diffs:
        if other.key == key:
            continue
        if any(fnmatch.fnmatch(other.key, pat) for pat in exclude_patterns):
            continue
        score = _similarity(baseline_value, other.baseline_value)
        if score >= min_similarity and score > best_score:
            best_score = score
            best_key = other.key
    return best_key, best_score


def chaperon_diffs(
    diffs: Sequence[KeyDiff],
    *,
    min_similarity: float = 0.6,
    exclude_patterns: Sequence[str] = (),
) -> List[ChaperondDiff]:
    """Return a list of ChaperondDiff with companion cross-references."""
    results: List[ChaperondDiff] = []
    for d in diffs:
        changed = d.baseline_value != d.target_value
        companion_key, companion_sim = _find_companion(
            d.key, d.baseline_value, diffs, min_similarity, exclude_patterns
        )
        results.append(
            ChaperondDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=changed,
                companion_key=companion_key,
                companion_similarity=companion_sim,
            )
        )
    return results
