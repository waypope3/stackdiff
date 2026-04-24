"""Pin specific keys in a diff result, marking them as protected from change."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import List, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class PinnedDiff:
    key: str
    baseline_value: object
    target_value: object
    changed: bool
    pinned: bool
    violation: bool  # True when pinned key has changed

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "pinned": self.pinned,
            "violation": self.violation,
        }

    def __str__(self) -> str:  # pragma: no cover
        marker = "[PINNED]" if self.pinned else ""
        flag = " *** VIOLATION ***" if self.violation else ""
        changed_str = "changed" if self.changed else "unchanged"
        return f"{self.key} ({changed_str}) {marker}{flag}"


def _is_pinned(key: str, patterns: Sequence[str]) -> bool:
    return any(fnmatch(key, p) for p in patterns)


def pin_diffs(
    diffs: List[KeyDiff],
    pinned_patterns: Sequence[str],
) -> List[PinnedDiff]:
    """Annotate each diff with pin status and flag violations.

    A *violation* occurs when a pinned key has changed (baseline != target
    and neither value is None indicating an addition/removal is also a
    violation for pinned keys).
    """
    result: List[PinnedDiff] = []
    for d in diffs:
        pinned = _is_pinned(d.key, pinned_patterns)
        changed = d.baseline_value != d.target_value
        violation = pinned and changed
        result.append(
            PinnedDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=changed,
                pinned=pinned,
                violation=violation,
            )
        )
    return result


def violations(pinned_diffs: List[PinnedDiff]) -> List[PinnedDiff]:
    """Return only the diffs that are pinned violations."""
    return [d for d in pinned_diffs if d.violation]
