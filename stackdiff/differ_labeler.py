"""Attach human-readable labels and metadata to diffs for display purposes."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from stackdiff.differ import KeyDiff


@dataclass
class LabeledDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    status: str
    label: str
    hint: str = ""

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "status": self.status,
            "label": self.label,
            "hint": self.hint,
        }


_STATUS_LABELS = {
    "changed": "Modified",
    "added": "Added",
    "removed": "Removed",
    "unchanged": "Unchanged",
}

_STATUS_HINTS = {
    "changed": "Value differs between baseline and target.",
    "added": "Key is present only in target.",
    "removed": "Key is present only in baseline.",
    "unchanged": "Values are identical.",
}


def _status(diff: KeyDiff) -> str:
    if diff.baseline_value is None:
        return "added"
    if diff.target_value is None:
        return "removed"
    if diff.baseline_value != diff.target_value:
        return "changed"
    return "unchanged"


def label_diffs(diffs: List[KeyDiff], custom_labels: Optional[dict] = None) -> List[LabeledDiff]:
    """Convert KeyDiff list into LabeledDiff list with status labels and hints."""
    labels = {**_STATUS_LABELS, **(custom_labels or {})}
    result = []
    for d in diffs:
        st = _status(d)
        result.append(LabeledDiff(
            key=d.key,
            baseline_value=d.baseline_value,
            target_value=d.target_value,
            status=st,
            label=labels.get(st, st.capitalize()),
            hint=_STATUS_HINTS.get(st, ""),
        ))
    return result
