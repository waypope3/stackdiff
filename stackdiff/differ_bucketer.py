"""Group diffs into named value-range buckets (e.g. short / medium / long)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class BucketSpec:
    """Definition of a single bucket: values whose length falls in [lo, hi)."""
    name: str
    lo: int = 0
    hi: Optional[int] = None  # None means unbounded


DEFAULT_BUCKETS: List[BucketSpec] = [
    BucketSpec("short", 0, 32),
    BucketSpec("medium", 32, 128),
    BucketSpec("long", 128, None),
]


@dataclass
class BucketedDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    bucket: str  # bucket name based on target_value length (or baseline if removed)

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "bucket": self.bucket,
        }

    def __str__(self) -> str:
        marker = "~" if self.changed else "="
        return f"[{marker}] {self.key!r:40s}  bucket={self.bucket}"


@dataclass
class BucketResult:
    diffs: List[BucketedDiff] = field(default_factory=list)
    buckets: dict = field(default_factory=dict)  # name -> List[BucketedDiff]

    def as_dict(self) -> dict:
        return {
            "buckets": {name: [d.as_dict() for d in items] for name, items in self.buckets.items()},
            "total": len(self.diffs),
        }


def _assign_bucket(value: Optional[str], specs: List[BucketSpec]) -> str:
    length = len(value) if value is not None else 0
    for spec in specs:
        if length >= spec.lo and (spec.hi is None or length < spec.hi):
            return spec.name
    return specs[-1].name if specs else "default"


def bucket_diffs(
    diffs: Sequence[KeyDiff],
    specs: Optional[List[BucketSpec]] = None,
) -> BucketResult:
    """Assign each diff to a bucket based on the length of its effective value."""
    if specs is None:
        specs = DEFAULT_BUCKETS

    result = BucketResult()
    bucket_map: dict = {spec.name: [] for spec in specs}

    for d in diffs:
        effective = d.target_value if d.target_value is not None else d.baseline_value
        name = _assign_bucket(effective, specs)
        bd = BucketedDiff(
            key=d.key,
            baseline_value=d.baseline_value,
            target_value=d.target_value,
            changed=d.baseline_value != d.target_value,
            bucket=name,
        )
        result.diffs.append(bd)
        bucket_map.setdefault(name, []).append(bd)

    result.buckets = bucket_map
    return result
