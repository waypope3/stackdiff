"""Split a flat list of KeyDiff results into named partitions based on key patterns."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class SplitPartition:
    name: str
    patterns: List[str]
    diffs: List[KeyDiff] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "patterns": self.patterns,
            "keys": [d.key for d in self.diffs],
            "count": len(self.diffs),
        }

    def __str__(self) -> str:  # pragma: no cover
        return f"SplitPartition({self.name!r}, count={len(self.diffs)})"


@dataclass
class SplitResult:
    partitions: List[SplitPartition]
    unmatched: List[KeyDiff] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "partitions": [p.as_dict() for p in self.partitions],
            "unmatched": [d.key for d in self.unmatched],
        }

    def by_name(self, name: str) -> SplitPartition | None:
        for p in self.partitions:
            if p.name == name:
                return p
        return None

    def __str__(self) -> str:  # pragma: no cover
        parts = ", ".join(p.name for p in self.partitions)
        return f"SplitResult(partitions=[{parts}], unmatched={len(self.unmatched)})"


def _matches_any(key: str, patterns: Sequence[str]) -> bool:
    return any(fnmatch.fnmatch(key, pat) for pat in patterns)


def split_diffs(
    diffs: Sequence[KeyDiff],
    partition_spec: Dict[str, List[str]],
) -> SplitResult:
    """Assign each KeyDiff to the first matching named partition.

    Args:
        diffs: Sequence of KeyDiff objects to partition.
        partition_spec: Ordered mapping of partition name -> list of glob patterns.
            A dict preserves insertion order (Python 3.7+), so the first matching
            partition wins.

    Returns:
        SplitResult with populated partitions and any unmatched diffs.
    """
    partitions = [
        SplitPartition(name=name, patterns=patterns)
        for name, patterns in partition_spec.items()
    ]
    unmatched: List[KeyDiff] = []

    for diff in diffs:
        placed = False
        for partition in partitions:
            if _matches_any(diff.key, partition.patterns):
                partition.diffs.append(diff)
                placed = True
                break
        if not placed:
            unmatched.append(diff)

    return SplitResult(partitions=partitions, unmatched=unmatched)
