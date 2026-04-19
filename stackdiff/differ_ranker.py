"""Rank diff keys by significance (change severity, alphabetical tiebreak)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from stackdiff.differ import KeyDiff


_STATUS_WEIGHT = {
    "removed": 4,
    "added": 3,
    "changed": 2,
    "unchanged": 1,
}


@dataclass
class RankedDiff:
    key: str
    diff: KeyDiff
    rank: int

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "rank": self.rank,
            "status": _status(self.diff),
        }


def _status(d: KeyDiff) -> str:
    if d.baseline is None:
        return "added"
    if d.target is None:
        return "removed"
    if d.baseline != d.target:
        return "changed"
    return "unchanged"


def rank_diffs(diffs: List[KeyDiff]) -> List[RankedDiff]:
    """Return diffs sorted by descending significance rank.

    Primary sort: status weight (removed > added > changed > unchanged).
    Secondary sort: key name alphabetically.
    """
    if not isinstance(diffs, list):
        raise TypeError("diffs must be a list")

    def _sort_key(d: KeyDiff):
        status = _status(d)
        weight = _STATUS_WEIGHT.get(status, 0)
        return (-weight, d.key)

    sorted_diffs = sorted(diffs, key=_sort_key)

    ranked: List[RankedDiff] = []
    for position, d in enumerate(sorted_diffs, start=1):
        ranked.append(RankedDiff(key=d.key, diff=d, rank=position))
    return ranked
