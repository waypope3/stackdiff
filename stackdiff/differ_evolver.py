"""differ_evolver: track how a key's value has evolved across multiple snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class EvolvedDiff:
    key: str
    history: List[Optional[str]]  # ordered oldest -> newest
    changed: bool
    first_seen: Optional[str]
    last_seen: Optional[str]
    change_count: int
    trend: str  # 'stable' | 'growing' | 'shrinking' | 'volatile'

    def as_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "history": self.history,
            "changed": self.changed,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "change_count": self.change_count,
            "trend": self.trend,
        }

    def __str__(self) -> str:  # pragma: no cover
        return (
            f"EvolvedDiff(key={self.key!r}, trend={self.trend}, "
            f"change_count={self.change_count})"
        )


def _detect_trend(history: List[Optional[str]]) -> str:
    """Infer a simple trend from the value history."""
    values = [v for v in history if v is not None]
    if len(values) <= 1:
        return "stable"
    lengths = [len(v) for v in values]
    changes = sum(1 for a, b in zip(history, history[1:]) if a != b)
    if changes == 0:
        return "stable"
    if changes >= len(history) - 1:
        return "volatile"
    if all(b >= a for a, b in zip(lengths, lengths[1:])):
        return "growing"
    if all(b <= a for a, b in zip(lengths, lengths[1:])):
        return "shrinking"
    return "volatile"


def evolve_diffs(
    snapshots: Sequence[Sequence[KeyDiff]],
) -> List[EvolvedDiff]:
    """Combine multiple ordered diff snapshots into per-key evolution records.

    Each element of *snapshots* is the full list of KeyDiff objects from one
    point in time, ordered oldest first.
    """
    if not snapshots:
        return []

    # Collect all keys across all snapshots.
    all_keys: List[str] = []
    seen: set = set()
    for snap in snapshots:
        for d in snap:
            if d.key not in seen:
                all_keys.append(d.key)
                seen.add(d.key)

    # Build a lookup: snap_index -> {key: value}
    index: List[Dict[str, Optional[str]]] = [
        {d.key: d.new_value for d in snap} for snap in snapshots
    ]

    results: List[EvolvedDiff] = []
    for key in all_keys:
        history = [snap.get(key) for snap in index]
        change_count = sum(
            1 for a, b in zip(history, history[1:]) if a != b
        )
        non_none = [v for v in history if v is not None]
        results.append(
            EvolvedDiff(
                key=key,
                history=history,
                changed=change_count > 0,
                first_seen=non_none[0] if non_none else None,
                last_seen=non_none[-1] if non_none else None,
                change_count=change_count,
                trend=_detect_trend(history),
            )
        )
    return results
