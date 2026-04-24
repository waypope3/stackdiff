"""Deduplicates a list of KeyDiff entries, keeping the last occurrence of each key."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from stackdiff.differ import KeyDiff


@dataclass
class DeduplicatedDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    duplicate_count: int  # how many times this key appeared before deduplication

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "duplicate_count": self.duplicate_count,
        }

    def __str__(self) -> str:
        marker = "~" if self.changed else "="
        dupe_note = f" (x{self.duplicate_count})" if self.duplicate_count > 1 else ""
        return f"[{marker}] {self.key}{dupe_note}: {self.baseline_value!r} -> {self.target_value!r}"


def deduplicate_diffs(diffs: List[KeyDiff]) -> List[DeduplicatedDiff]:
    """Return a deduplicated list of KeyDiff entries.

    When a key appears more than once the *last* entry wins.  The
    ``duplicate_count`` field records how many times the key was seen in the
    original list so callers can surface a warning if desired.

    Args:
        diffs: Ordered list of KeyDiff instances (may contain duplicate keys).

    Returns:
        List of DeduplicatedDiff instances in first-seen key order.
    """
    seen: dict[str, int] = {}  # key -> count
    latest: dict[str, KeyDiff] = {}  # key -> last KeyDiff
    order: list[str] = []  # preserves first-seen insertion order

    for d in diffs:
        if d.key not in seen:
            order.append(d.key)
            seen[d.key] = 0
        seen[d.key] += 1
        latest[d.key] = d

    result: list[DeduplicatedDiff] = []
    for key in order:
        kd = latest[key]
        result.append(
            DeduplicatedDiff(
                key=kd.key,
                baseline_value=kd.baseline_value,
                target_value=kd.target_value,
                changed=kd.baseline_value != kd.target_value,
                duplicate_count=seen[key],
            )
        )
    return result
