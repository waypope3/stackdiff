"""Score a diff result to indicate overall change severity."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List
from stackdiff.differ import KeyDiff


@dataclass
class DiffScore:
    total: int
    changed: int
    added: int
    removed: int
    score: float  # 0.0 (no change) – 1.0 (everything changed)
    severity: str  # none | low | medium | high

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "changed": self.changed,
            "added": self.added,
            "removed": self.removed,
            "score": round(self.score, 4),
            "severity": self.severity,
        }

    def __str__(self) -> str:
        return (
            f"severity={self.severity} score={self.score:.2%} "
            f"(changed={self.changed} added={self.added} removed={self.removed} total={self.total})"
        )


def _severity(score: float) -> str:
    if score == 0.0:
        return "none"
    if score < 0.25:
        return "low"
    if score < 0.60:
        return "medium"
    return "high"


def score_diffs(diffs: List[KeyDiff]) -> DiffScore:
    """Compute a severity score for a list of KeyDiff entries."""
    total = len(diffs)
    changed = sum(1 for d in diffs if d.status == "changed")
    added = sum(1 for d in diffs if d.status == "added")
    removed = sum(1 for d in diffs if d.status == "removed")
    dirty = changed + added + removed
    score = dirty / total if total > 0 else 0.0
    return DiffScore(
        total=total,
        changed=changed,
        added=added,
        removed=removed,
        score=score,
        severity=_severity(score),
    )
