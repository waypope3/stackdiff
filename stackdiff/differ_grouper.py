"""Group diffs by status (changed, added, removed, unchanged)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from stackdiff.differ import KeyDiff


@dataclass
class GroupedDiffs:
    changed: List[KeyDiff] = field(default_factory=list)
    added: List[KeyDiff] = field(default_factory=list)
    removed: List[KeyDiff] = field(default_factory=list)
    unchanged: List[KeyDiff] = field(default_factory=list)

    def as_dict(self) -> Dict[str, List[KeyDiff]]:
        return {
            "changed": self.changed,
            "added": self.added,
            "removed": self.removed,
            "unchanged": self.unchanged,
        }

    def total(self) -> int:
        return len(self.changed) + len(self.added) + len(self.removed) + len(self.unchanged)

    def has_differences(self) -> bool:
        """Return True if any diffs are non-unchanged (i.e. something actually changed)."""
        return bool(self.changed or self.added or self.removed)

    def __str__(self) -> str:
        return (
            f"GroupedDiffs(changed={len(self.changed)}, added={len(self.added)}, "
            f"removed={len(self.removed)}, unchanged={len(self.unchanged)})"
        )


def group_diffs(diffs: List[KeyDiff]) -> GroupedDiffs:
    """Partition a flat list of KeyDiff into a GroupedDiffs by status."""
    groups = GroupedDiffs()
    for d in diffs:
        if d.baseline is None:
            groups.added.append(d)
        elif d.current is None:
            groups.removed.append(d)
        elif d.baseline != d.current:
            groups.changed.append(d)
        else:
            groups.unchanged.append(d)
    return groups
