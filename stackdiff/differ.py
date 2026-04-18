"""Core diffing logic for stackdiff."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class KeyDiff:
    baseline: Optional[str]
    target: Optional[str]
    status: str  # 'changed' | 'unchanged' | 'added' | 'removed'


# DiffResult maps output key -> KeyDiff
DiffResult = Dict[str, KeyDiff]


def has_diff(result: DiffResult) -> bool:
    """Return True if any key has a non-unchanged status."""
    return any(v.status != "unchanged" for v in result.values())


def summary(result: DiffResult) -> dict:
    """Return counts by status."""
    counts: dict = {"changed": 0, "added": 0, "removed": 0, "unchanged": 0}
    for v in result.values():
        counts[v.status] = counts.get(v.status, 0) + 1
    return counts


def diff_stacks(baseline: dict, target: dict) -> DiffResult:
    """Produce a DiffResult comparing two flat output dicts."""
    result: DiffResult = {}
    all_keys = set(baseline) | set(target)
    for key in all_keys:
        b_val = baseline.get(key)
        t_val = target.get(key)
        if key not in baseline:
            status = "added"
        elif key not in target:
            status = "removed"
        elif b_val != t_val:
            status = "changed"
        else:
            status = "unchanged"
        result[key] = KeyDiff(baseline=b_val, target=t_val, status=status)
    return result
