"""differ_comparator: side-by-side value comparison with change magnitude."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from stackdiff.differ import KeyDiff


@dataclass
class ComparedDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    magnitude: str  # 'none' | 'minor' | 'major' | 'added' | 'removed'
    shared_prefix: str

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "magnitude": self.magnitude,
            "shared_prefix": self.shared_prefix,
        }

    def __str__(self) -> str:
        marker = "~" if self.changed else "="
        return (
            f"[{marker}] {self.key}: "
            f"{self.baseline_value!r} -> {self.target_value!r} "
            f"({self.magnitude})"
        )


def _shared_prefix(a: str, b: str) -> str:
    """Return the longest common leading substring of a and b."""
    result = []
    for ca, cb in zip(a, b):
        if ca == cb:
            result.append(ca)
        else:
            break
    return "".join(result)


def _magnitude(baseline: Optional[str], target: Optional[str]) -> str:
    """Compute the change magnitude between two optional string values.

    Returns one of:
      - 'added'   : baseline is absent, target is present
      - 'removed' : baseline is present, target is absent
      - 'none'    : values are identical
      - 'minor'   : values differ but share >= 50% prefix similarity
      - 'major'   : values differ with < 50% prefix similarity
    """
    if baseline is None:
        return "added"
    if target is None:
        return "removed"
    if baseline == target:
        return "none"
    b_len = len(baseline)
    t_len = len(target)
    prefix_len = len(_shared_prefix(baseline, target))
    similarity = (2 * prefix_len) / (b_len + t_len) if (b_len + t_len) > 0 else 1.0
    return "minor" if similarity >= 0.5 else "major"


def compare_diffs(diffs: List[KeyDiff]) -> List[ComparedDiff]:
    """Annotate each KeyDiff with side-by-side comparison metadata."""
    result: List[ComparedDiff] = []
    for d in diffs:
        bv = d.baseline_value
        tv = d.target_value
        mag = _magnitude(bv, tv)
        prefix = _shared_prefix(bv or "", tv or "")
        result.append(
            ComparedDiff(
                key=d.key,
                baseline_value=bv,
                target_value=tv,
                changed=d.baseline_value != d.target_value,
                magnitude=mag,
                shared_prefix=prefix,
            )
        )
    return result


def filter_by_magnitude(diffs: List[ComparedDiff], *magnitudes: str) -> List[ComparedDiff]:
    """Return only the ComparedDiff entries whose magnitude matches one of the given values.

    Example::

        major_changes = filter_by_magnitude(results, "major", "added", "removed")
    """
    allowed = set(magnitudes)
    return [d for d in diffs if d.magnitude in allowed]
