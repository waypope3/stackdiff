"""Tag diffs with arbitrary metadata labels based on key patterns."""
from __future__ import annotations

fnmatch = __import__("fnmatch").fnmatch
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.differ import KeyDiff


@dataclass
class TaggedDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    status: str
    tags: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "status": self.status,
            "tags": self.tags,
        }


def _status(d: KeyDiff) -> str:
    if d.baseline_value is None:
        return "added"
    if d.target_value is None:
        return "removed"
    if d.baseline_value != d.target_value:
        return "changed"
    return "unchanged"


def tag_diffs(
    diffs: List[KeyDiff],
    tag_rules: Dict[str, List[str]],
) -> List[TaggedDiff]:
    """Apply tag_rules {tag: [pattern, ...]} to each diff by key matching.

    Args:
        diffs: list of KeyDiff results from diff_stacks.
        tag_rules: mapping of tag name to list of glob patterns matched against key.

    Returns:
        List of TaggedDiff with zero or more tags per entry.
    """
    tagged: List[TaggedDiff] = []
    for d in diffs:
        applied: List[str] = []
        for tag, patterns in tag_rules.items():
            if any(fnmatch(d.key, p) for p in patterns):
                applied.append(tag)
        tagged.append(
            TaggedDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                status=_status(d),
                tags=sorted(applied),
            )
        )
    return tagged
