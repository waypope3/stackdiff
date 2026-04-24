"""Prune diffs by removing entries that match suppression rules.

A suppression rule is a mapping of key pattern → value pattern. A diff
entry is pruned (excluded from output) when *both* its key and its
baseline/target values match the corresponding patterns.

This is useful for ignoring well-known noise such as auto-generated
ARN suffixes or timestamp fields that always differ.
"""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from stackdiff.differ import KeyDiff


@dataclass(frozen=True)
class PruneRule:
    """A single suppression rule."""
    key_pattern: str
    value_pattern: str = "*"


@dataclass
class PrunedDiff:
    """Wrapper around a KeyDiff annotated with pruning metadata."""
    diff: KeyDiff
    pruned: bool
    matched_rule: PruneRule | None = field(default=None)

    def as_dict(self) -> dict:
        return {
            "key": self.diff.key,
            "baseline": self.diff.baseline,
            "target": self.diff.target,
            "pruned": self.pruned,
            "matched_rule": (
                {"key_pattern": self.matched_rule.key_pattern,
                 "value_pattern": self.matched_rule.value_pattern}
                if self.matched_rule else None
            ),
        }

    def __str__(self) -> str:
        tag = " [pruned]" if self.pruned else ""
        return f"{self.diff.key}: {self.diff.baseline!r} -> {self.diff.target!r}{tag}"


def _matches_rule(diff: KeyDiff, rule: PruneRule) -> bool:
    """Return True when *diff* satisfies *rule*."""
    if not fnmatch.fnmatch(diff.key, rule.key_pattern):
        return False
    for value in (diff.baseline, diff.target):
        if value is None:
            continue
        if not fnmatch.fnmatch(str(value), rule.value_pattern):
            return False
    return True


def prune_diffs(
    diffs: Iterable[KeyDiff],
    rules: Sequence[PruneRule],
) -> list[PrunedDiff]:
    """Annotate *diffs* with pruning information based on *rules*.

    Entries that match at least one rule are marked ``pruned=True``.
    The caller decides whether to filter them out or keep them for
    audit purposes.
    """
    result: list[PrunedDiff] = []
    for diff in diffs:
        matched: PruneRule | None = None
        for rule in rules:
            if _matches_rule(diff, rule):
                matched = rule
                break
        result.append(PrunedDiff(diff=diff, pruned=matched is not None, matched_rule=matched))
    return result


def active_diffs(pruned: Iterable[PrunedDiff]) -> list[PrunedDiff]:
    """Return only the non-pruned entries."""
    return [p for p in pruned if not p.pruned]
