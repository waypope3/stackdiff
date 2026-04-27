"""differ_cadence: measure how frequently each key changes across a series of diff snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from stackdiff.differ import KeyDiff


@dataclass
class CadencedDiff:
    key: str
    baseline_value: str
    target_value: str
    changed: bool
    appearances: int        # number of snapshots the key appeared in
    change_count: int       # number of snapshots where the key differed
    cadence: float          # change_count / appearances  (0.0 – 1.0)
    stability: str          # "stable" | "moderate" | "volatile"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "appearances": self.appearances,
            "change_count": self.change_count,
            "cadence": round(self.cadence, 4),
            "stability": self.stability,
        }

    def __str__(self) -> str:
        marker = "~" if self.changed else "="
        return (
            f"[{marker}] {self.key}  cadence={self.cadence:.2f}"
            f"  ({self.change_count}/{self.appearances})  [{self.stability}]"
        )


def _stability(cadence: float) -> str:
    if cadence == 0.0:
        return "stable"
    if cadence <= 0.4:
        return "moderate"
    return "volatile"


def cadence_diffs(
    history: Iterable[List[KeyDiff]],
    current: List[KeyDiff],
) -> List[CadencedDiff]:
    """Compute per-key change cadence from *history* snapshots and annotate *current* diffs.

    Args:
        history: An iterable of past diff lists (oldest first).  Each list is
                 the result of a previous ``diff_stacks`` call.
        current: The most-recent diff list to annotate.

    Returns:
        A list of :class:`CadencedDiff` instances in the same order as *current*.
    """
    # Accumulate per-key stats across all historical snapshots.
    appearances: dict[str, int] = {}
    changes: dict[str, int] = {}

    for snapshot in history:
        for d in snapshot:
            appearances[d.key] = appearances.get(d.key, 0) + 1
            if d.baseline_value != d.target_value:
                changes[d.key] = changes.get(d.key, 0) + 1

    result: List[CadencedDiff] = []
    for d in current:
        app = appearances.get(d.key, 0)
        chg = changes.get(d.key, 0)
        cad = chg / app if app > 0 else 0.0
        result.append(
            CadencedDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=d.baseline_value != d.target_value,
                appearances=app,
                change_count=chg,
                cadence=cad,
                stability=_stability(cad),
            )
        )
    return result
