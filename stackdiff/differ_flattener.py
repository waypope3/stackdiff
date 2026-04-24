"""Flatten nested diff results into a single-level list with dot-notation keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List

from stackdiff.differ import KeyDiff


@dataclass
class FlattenedDiff:
    key: str
    baseline_value: Any
    target_value: Any
    changed: bool
    depth: int

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "depth": self.depth,
        }

    def __str__(self) -> str:  # pragma: no cover
        marker = "~" if self.changed else "="
        return f"[{marker}] {self.key}: {self.baseline_value!r} -> {self.target_value!r}"


def _dot_join(parent: str, child: str) -> str:
    return f"{parent}.{child}" if parent else child


def _flatten_value(
    key: str,
    baseline: Any,
    target: Any,
    depth: int,
    results: List[FlattenedDiff],
) -> None:
    """Recursively flatten dict values; emit a FlattenedDiff for leaf nodes."""
    if isinstance(baseline, dict) and isinstance(target, dict):
        all_keys = sorted(set(baseline) | set(target))
        for k in all_keys:
            _flatten_value(
                _dot_join(key, k),
                baseline.get(k),
                target.get(k),
                depth + 1,
                results,
            )
    else:
        results.append(
            FlattenedDiff(
                key=key,
                baseline_value=baseline,
                target_value=target,
                changed=baseline != target,
                depth=depth,
            )
        )


def flatten_diffs(diffs: List[KeyDiff]) -> List[FlattenedDiff]:
    """Convert a list of KeyDiff objects into a flat list of FlattenedDiff objects.

    Values that are themselves dicts are recursively expanded with dot-notation keys.
    """
    results: List[FlattenedDiff] = []
    for d in diffs:
        _flatten_value(d.key, d.baseline_value, d.target_value, 0, results)
    return results
