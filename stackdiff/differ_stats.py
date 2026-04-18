"""Compute statistical metrics from a diff result."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from stackdiff.differ import KeyDiff


@dataclass
class DiffStats:
    total: int
    changed: int
    added: int
    removed: int
    unchanged: int
    change_rate: float  # fraction of keys that differ (0.0-1.0)

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "changed": self.changed,
            "added": self.added,
            "removed": self.removed,
            "unchanged": self.unchanged,
            "change_rate": round(self.change_rate, 4),
        }

    def __str__(self) -> str:
        pct = f"{self.change_rate * 100:.1f}%"
        return (
            f"total={self.total} changed={self.changed} "
            f"added={self.added} removed={self.removed} "
            f"unchanged={self.unchanged} change_rate={pct}"
        )


def compute_stats(diffs: List[KeyDiff]) -> DiffStats:
    """Return a DiffStats instance computed from *diffs*."""
    changed = sum(1 for d in diffs if d.baseline is not None and d.target is not None and d.baseline != d.target)
    added = sum(1 for d in diffs if d.baseline is None and d.target is not None)
    removed = sum(1 for d in diffs if d.baseline is not None and d.target is None)
    unchanged = sum(1 for d in diffs if d.baseline == d.target)
    total = len(diffs)
    differing = changed + added + removed
    change_rate = differing / total if total else 0.0
    return DiffStats(
        total=total,
        changed=changed,
        added=added,
        removed=removed,
        unchanged=unchanged,
        change_rate=change_rate,
    )
