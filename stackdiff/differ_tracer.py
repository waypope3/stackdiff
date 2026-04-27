"""Trace the lineage of a diff key across multiple stack snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class TraceEntry:
    snapshot_id: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool

    def as_dict(self) -> dict:
        return {
            "snapshot_id": self.snapshot_id,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
        }


@dataclass
class TracedDiff:
    key: str
    history: List[TraceEntry] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return sum(1 for e in self.history if e.changed)

    @property
    def ever_changed(self) -> bool:
        return self.total_changes > 0

    @property
    def latest(self) -> Optional[TraceEntry]:
        return self.history[-1] if self.history else None

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "total_changes": self.total_changes,
            "ever_changed": self.ever_changed,
            "history": [e.as_dict() for e in self.history],
        }

    def __str__(self) -> str:
        return (
            f"TracedDiff(key={self.key!r}, "
            f"total_changes={self.total_changes}, "
            f"snapshots={len(self.history)})"
        )


def trace_diffs(
    snapshots: Sequence[tuple[str, List[KeyDiff]]],
) -> List[TracedDiff]:
    """Build per-key traces across an ordered sequence of (snapshot_id, diffs).

    Args:
        snapshots: Ordered pairs of snapshot identifier and the list of
                   KeyDiff objects produced for that snapshot.

    Returns:
        A list of TracedDiff objects, one per unique key seen across all
        snapshots, ordered by first appearance.
    """
    traces: dict[str, TracedDiff] = {}

    for snapshot_id, diffs in snapshots:
        for kd in diffs:
            if kd.key not in traces:
                traces[kd.key] = TracedDiff(key=kd.key)
            entry = TraceEntry(
                snapshot_id=snapshot_id,
                baseline_value=kd.baseline,
                target_value=kd.target,
                changed=kd.baseline != kd.target,
            )
            traces[kd.key].history.append(entry)

    return list(traces.values())
