"""Freeze diffs by marking which keys have been explicitly pinned as stable.

A 'frozen' key is one where the operator declares the value acceptable as-is;
changes to frozen keys are surfaced but flagged so downstream tooling can
treat them differently (e.g. suppress alerts, dim output).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import List, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class FrozenDiff:
    key: str
    baseline_value: str
    target_value: str
    changed: bool
    frozen: bool
    freeze_pattern: str | None = field(default=None)

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "frozen": self.frozen,
            "freeze_pattern": self.freeze_pattern,
        }

    def __str__(self) -> str:  # pragma: no cover
        marker = "❄" if self.frozen else " "
        diff_marker = "~" if self.changed else "="
        return f"[{diff_marker}][{marker}] {self.key}: {self.baseline_value!r} -> {self.target_value!r}"


def _matches_freeze(key: str, patterns: Sequence[str]) -> str | None:
    """Return the first matching pattern, or None."""
    for pattern in patterns:
        if fnmatch(key, pattern):
            return pattern
    return None


def freeze_diffs(
    diffs: List[KeyDiff],
    freeze_patterns: Sequence[str] | None = None,
) -> List[FrozenDiff]:
    """Wrap each KeyDiff in a FrozenDiff, marking keys matched by *freeze_patterns*.

    Args:
        diffs: Raw diff results from :func:`stackdiff.differ.diff_stacks`.
        freeze_patterns: Glob patterns.  Keys matching any pattern are frozen.

    Returns:
        A list of :class:`FrozenDiff` instances in the same order as *diffs*.
    """
    patterns: Sequence[str] = freeze_patterns or []
    result: List[FrozenDiff] = []
    for d in diffs:
        changed = d.baseline_value != d.target_value
        matched = _matches_freeze(d.key, patterns)
        result.append(
            FrozenDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=changed,
                frozen=matched is not None,
                freeze_pattern=matched,
            )
        )
    return result
