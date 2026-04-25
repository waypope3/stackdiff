"""Partition diffs into buckets based on a key predicate or pattern map."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from stackdiff.differ import KeyDiff


@dataclass
class PartitionedDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    bucket: str

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "bucket": self.bucket,
        }

    def __str__(self) -> str:  # pragma: no cover
        marker = "~" if self.changed else "="
        return f"[{self.bucket}] {marker} {self.key}: {self.baseline_value!r} -> {self.target_value!r}"


@dataclass
class PartitionResult:
    buckets: Dict[str, List[PartitionedDiff]] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {k: [d.as_dict() for d in v] for k, v in self.buckets.items()}

    def all_diffs(self) -> List[PartitionedDiff]:
        return [d for diffs in self.buckets.values() for d in diffs]

    def changed_in(self, bucket: str) -> List[PartitionedDiff]:
        return [d for d in self.buckets.get(bucket, []) if d.changed]


def _resolve_bucket(
    key: str,
    patterns: Dict[str, List[str]],
    fallback: str,
) -> str:
    for bucket, globs in patterns.items():
        for glob in globs:
            if fnmatch.fnmatch(key.lower(), glob.lower()):
                return bucket
    return fallback


def partition_diffs(
    diffs: List[KeyDiff],
    patterns: Dict[str, List[str]],
    fallback: str = "other",
    predicate: Optional[Callable[[KeyDiff], str]] = None,
) -> PartitionResult:
    """Assign each KeyDiff to a named bucket.

    Resolution order: *predicate* (if provided) then *patterns* glob map,
    then *fallback*.
    """
    result: Dict[str, List[PartitionedDiff]] = {}

    for diff in diffs:
        if predicate is not None:
            bucket = predicate(diff)
        else:
            bucket = _resolve_bucket(diff.key, patterns, fallback)

        changed = diff.baseline_value != diff.target_value
        pd = PartitionedDiff(
            key=diff.key,
            baseline_value=diff.baseline_value,
            target_value=diff.target_value,
            changed=changed,
            bucket=bucket,
        )
        result.setdefault(bucket, []).append(pd)

    return PartitionResult(buckets=result)
