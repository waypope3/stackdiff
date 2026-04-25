"""Pivot diffs by a chosen dimension (status, key-prefix, or value-type)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal

from stackdiff.differ import KeyDiff

PivotDimension = Literal["status", "prefix", "value_type"]


@dataclass
class PivotBucket:
    dimension: str
    label: str
    diffs: List[KeyDiff] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "label": self.label,
            "count": len(self.diffs),
            "keys": [d.key for d in self.diffs],
        }

    def __str__(self) -> str:  # pragma: no cover
        return f"PivotBucket({self.label!r}, count={len(self.diffs)})"


@dataclass
class PivotResult:
    dimension: PivotDimension
    buckets: Dict[str, PivotBucket] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "buckets": {k: v.as_dict() for k, v in self.buckets.items()},
        }

    def __str__(self) -> str:  # pragma: no cover
        labels = list(self.buckets.keys())
        return f"PivotResult(dimension={self.dimension!r}, buckets={labels})"


def _status_label(d: KeyDiff) -> str:
    if d.baseline_value is None:
        return "added"
    if d.target_value is None:
        return "removed"
    if d.baseline_value != d.target_value:
        return "changed"
    return "unchanged"


def _prefix_label(d: KeyDiff) -> str:
    parts = d.key.split("_", 1)
    return parts[0].lower() if len(parts) > 1 else "other"


def _value_type_label(d: KeyDiff) -> str:
    value = d.target_value if d.target_value is not None else d.baseline_value
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float"
    s = str(value)
    if s.startswith("arn:"):
        return "arn"
    if s.startswith(("http://", "https://")):
        return "url"
    return "string"


_LABELERS = {
    "status": _status_label,
    "prefix": _prefix_label,
    "value_type": _value_type_label,
}


def pivot_diffs(diffs: List[KeyDiff], dimension: PivotDimension = "status") -> PivotResult:
    """Group *diffs* into buckets according to *dimension*."""
    if dimension not in _LABELERS:
        raise ValueError(f"Unknown pivot dimension {dimension!r}")
    labeler = _LABELERS[dimension]
    result = PivotResult(dimension=dimension)
    for d in diffs:
        label = labeler(d)
        if label not in result.buckets:
            result.buckets[label] = PivotBucket(dimension=dimension, label=label)
        result.buckets[label].diffs.append(d)
    return result
