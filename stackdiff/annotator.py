"""Annotate diff keys with human-readable change descriptions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from stackdiff.differ import KeyDiff


@dataclass
class AnnotatedDiff:
    key: str
    baseline: str | None
    target: str | None
    status: str  # changed | added | removed | unchanged
    annotation: str


def _status(diff: KeyDiff) -> str:
    if diff.baseline is None:
        return "added"
    if diff.target is None:
        return "removed"
    if diff.baseline != diff.target:
        return "changed"
    return "unchanged"


def _annotate(diff: KeyDiff, status: str) -> str:
    if status == "added":
        return f"Key '{diff.key}' is new in target (value: {diff.target!r})"
    if status == "removed":
        return f"Key '{diff.key}' was removed from target (was: {diff.baseline!r})"
    if status == "changed":
        return (
            f"Key '{diff.key}' changed from {diff.baseline!r} to {diff.target!r}"
        )
    return f"Key '{diff.key}' is unchanged (value: {diff.baseline!r})"


def annotate_diffs(diffs: List[KeyDiff]) -> List[AnnotatedDiff]:
    """Return an AnnotatedDiff for every KeyDiff in *diffs*."""
    result: List[AnnotatedDiff] = []
    for diff in diffs:
        status = _status(diff)
        result.append(
            AnnotatedDiff(
                key=diff.key,
                baseline=diff.baseline,
                target=diff.target,
                status=status,
                annotation=_annotate(diff, status),
            )
        )
    return result
