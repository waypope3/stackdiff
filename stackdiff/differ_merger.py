"""Merge two diff results into a single unified view."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from stackdiff.differ import KeyDiff


@dataclass
class MergedDiff:
    key: str
    baseline_diff: KeyDiff | None
    target_diff: KeyDiff | None

    @property
    def status(self) -> str:
        if self.baseline_diff is None:
            return "new_in_target"
        if self.target_diff is None:
            return "only_in_baseline"
        if self.baseline_diff.old == self.target_diff.old and self.baseline_diff.new == self.target_diff.new:
            return "same"
        return "diverged"


@dataclass
class MergeResult:
    merged: List[MergedDiff] = field(default_factory=list)

    def by_status(self, status: str) -> List[MergedDiff]:
        return [m for m in self.merged if m.status == status]

    def has_divergence(self) -> bool:
        return any(m.status == "diverged" for m in self.merged)


def merge_diffs(
    baseline_diffs: List[KeyDiff],
    target_diffs: List[KeyDiff],
) -> MergeResult:
    """Merge two lists of KeyDiff by key name."""
    baseline_map: Dict[str, KeyDiff] = {d.key: d for d in baseline_diffs}
    target_map: Dict[str, KeyDiff] = {d.key: d for d in target_diffs}
    all_keys = sorted(set(baseline_map) | set(target_map))
    merged = [
        MergedDiff(
            key=k,
            baseline_diff=baseline_map.get(k),
            target_diff=target_map.get(k),
        )
        for k in all_keys
    ]
    return MergeResult(merged=merged)
