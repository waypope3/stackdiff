"""Summarise a diff result into high-level statistics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from stackdiff.differ import KeyDiff


@dataclass
class DiffSummary:
    total: int
    changed: int
    added: int
    removed: int
    unchanged: int

    @property
    def has_diff(self) -> bool:
        return (self.changed + self.added + self.removed) > 0

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "changed": self.changed,
            "added": self.added,
            "removed": self.removed,
            "unchanged": self.unchanged,
        }

    def __str__(self) -> str:
        parts = []
        if self.changed:
            parts.append(f"{self.changed} changed")
        if self.added:
            parts.append(f"{self.added} added")
        if self.removed:
            parts.append(f"{self.removed} removed")
        if not parts:
            return f"{self.total} key(s), no differences"
        return f"{self.total} key(s): " + ", ".join(parts)


def summarise(diffs: Sequence[KeyDiff]) -> DiffSummary:
    """Return a DiffSummary for the given sequence of KeyDiff objects."""
    changed = sum(1 for d in diffs if d.baseline is not None and d.target is not None and d.baseline != d.target)
    added = sum(1 for d in diffs if d.baseline is None and d.target is not None)
    removed = sum(1 for d in diffs if d.baseline is not None and d.target is None)
    unchanged = sum(1 for d in diffs if d.baseline == d.target)
    return DiffSummary(
        total=len(diffs),
        changed=changed,
        added=added,
        removed=removed,
        unchanged=unchanged,
    )
