"""Index diffs by multiple dimensions for fast lookup and cross-referencing."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.differ import KeyDiff


@dataclass
class IndexedDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    index: int  # position in original list
    status: str  # 'changed' | 'added' | 'removed' | 'unchanged'

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "index": self.index,
            "status": self.status,
        }

    def __str__(self) -> str:
        marker = "~" if self.changed else "="
        return f"[{self.index:03d}] {marker} {self.key}"


@dataclass
class DiffIndex:
    by_key: Dict[str, IndexedDiff] = field(default_factory=dict)
    by_status: Dict[str, List[IndexedDiff]] = field(default_factory=dict)
    ordered: List[IndexedDiff] = field(default_factory=list)

    def lookup(self, key: str) -> Optional[IndexedDiff]:
        return self.by_key.get(key)

    def with_status(self, status: str) -> List[IndexedDiff]:
        return self.by_status.get(status, [])

    def __len__(self) -> int:
        return len(self.ordered)


def _status(diff: KeyDiff) -> str:
    if diff.baseline_value is None:
        return "added"
    if diff.target_value is None:
        return "removed"
    if diff.baseline_value != diff.target_value:
        return "changed"
    return "unchanged"


def index_diffs(diffs: List[KeyDiff]) -> DiffIndex:
    """Build a DiffIndex from a flat list of KeyDiff objects."""
    idx = DiffIndex()
    for position, d in enumerate(diffs):
        status = _status(d)
        entry = IndexedDiff(
            key=d.key,
            baseline_value=d.baseline_value,
            target_value=d.target_value,
            changed=d.baseline_value != d.target_value,
            index=position,
            status=status,
        )
        idx.ordered.append(entry)
        idx.by_key[d.key] = entry
        idx.by_status.setdefault(status, []).append(entry)
    return idx
