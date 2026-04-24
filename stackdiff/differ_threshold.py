"""Threshold filtering for diffs — suppress changes below a significance level."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from stackdiff.differ import KeyDiff


@dataclass
class ThresholdOptions:
    """Controls which diffs survive threshold filtering."""

    # Minimum string-edit distance (inclusive) to keep a CHANGED entry.
    # 0 means keep everything.
    min_edit_distance: int = 0
    # If True, always keep ADDED / REMOVED keys regardless of edit distance.
    keep_structural: bool = True


@dataclass
class ThresholdedDiff:
    """A KeyDiff decorated with edit-distance metadata."""

    key: str
    baseline_value: str | None
    target_value: str | None
    changed: bool
    edit_distance: int
    suppressed: bool

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "edit_distance": self.edit_distance,
            "suppressed": self.suppressed,
        }


def _edit_distance(a: str | None, b: str | None) -> int:
    """Simple Levenshtein distance between two strings."""
    s1 = str(a) if a is not None else ""
    s2 = str(b) if b is not None else ""
    if s1 == s2:
        return 0
    rows, cols = len(s1) + 1, len(s2) + 1
    prev = list(range(cols))
    for i, c1 in enumerate(s1, 1):
        curr = [i] + [0] * (cols - 1)
        for j, c2 in enumerate(s2, 1):
            curr[j] = min(
                prev[j] + 1,
                curr[j - 1] + 1,
                prev[j - 1] + (0 if c1 == c2 else 1),
            )
        prev = curr
    return prev[-1]


def _is_structural(diff: KeyDiff) -> bool:
    """True when the diff represents an addition or removal (not a change)."""
    return diff.baseline_value is None or diff.target_value is None


def apply_threshold(
    diffs: Sequence[KeyDiff],
    options: ThresholdOptions | None = None,
) -> list[ThresholdedDiff]:
    """Annotate *diffs* with edit-distance and mark entries that fall below the threshold."""
    opts = options or ThresholdOptions()
    result: list[ThresholdedDiff] = []
    for d in diffs:
        dist = _edit_distance(d.baseline_value, d.target_value)
        structural = _is_structural(d)
        if opts.min_edit_distance > 0 and d.changed:
            if structural and opts.keep_structural:
                suppressed = False
            else:
                suppressed = dist < opts.min_edit_distance
        else:
            suppressed = False
        result.append(
            ThresholdedDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=d.changed,
                edit_distance=dist,
                suppressed=suppressed,
            )
        )
    return result
