"""differ_censor: suppress diffs whose magnitude falls below a minimum edit threshold.

Useful for ignoring trivial whitespace or timestamp noise between environments.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from stackdiff.differ import KeyDiff


@dataclass
class CensoredDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    censored: bool  # True when a real diff was suppressed
    reason: Optional[str] = field(default=None)

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "censored": self.censored,
            "reason": self.reason,
        }

    def __str__(self) -> str:
        marker = "~" if self.censored else ("*" if self.changed else " ")
        return f"[{marker}] {self.key}: {self.baseline_value!r} -> {self.target_value!r}"


def _edit_distance(a: str, b: str) -> int:
    """Simple Levenshtein distance between two strings."""
    if a == b:
        return 0
    la, lb = len(a), len(b)
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * lb
        for j, cb in enumerate(b, 1):
            curr[j] = min(
                prev[j] + 1,
                curr[j - 1] + 1,
                prev[j - 1] + (0 if ca == cb else 1),
            )
        prev = curr
    return prev[lb]


def censor_diffs(
    diffs: List[KeyDiff],
    min_edit_distance: int = 2,
    censor_patterns: Optional[List[str]] = None,
) -> List[CensoredDiff]:
    """Return CensoredDiff list, suppressing changes below *min_edit_distance*.

    Args:
        diffs: raw KeyDiff list from differ.diff_stacks.
        min_edit_distance: changes with an edit distance strictly less than
            this value are marked censored (changed=False).
        censor_patterns: optional list of key glob patterns whose changes are
            always censored regardless of distance.
    """
    import fnmatch

    patterns = censor_patterns or []
    result: List[CensoredDiff] = []

    for d in diffs:
        raw_changed = d.baseline_value != d.target_value
        censored = False
        reason: Optional[str] = None

        if raw_changed:
            # Pattern-based censoring takes priority
            for pat in patterns:
                if fnmatch.fnmatch(d.key, pat):
                    censored = True
                    reason = f"key matches censor pattern '{pat}'"
                    break

            if not censored:
                bv = d.baseline_value or ""
                tv = d.target_value or ""
                dist = _edit_distance(bv, tv)
                if dist < min_edit_distance:
                    censored = True
                    reason = f"edit distance {dist} < threshold {min_edit_distance}"

        result.append(
            CensoredDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=raw_changed and not censored,
                censored=censored,
                reason=reason,
            )
        )

    return result
