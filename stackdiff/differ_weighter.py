"""Assign importance weights to diffs based on key patterns and change type."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from stackdiff.differ import KeyDiff

# Default weight rules: (glob_pattern, weight)
_DEFAULT_RULES: List[Tuple[str, float]] = [
    ("*password*", 3.0),
    ("*secret*", 3.0),
    ("*token*", 2.5),
    ("*key*", 2.0),
    ("*arn*", 1.5),
    ("*endpoint*", 1.5),
    ("*url*", 1.2),
]

_CHANGE_TYPE_MULTIPLIER = {"changed": 1.0, "added": 0.8, "removed": 1.2, "unchanged": 0.0}


@dataclass
class WeightedDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    weight: float
    matched_rule: Optional[str]

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "weight": self.weight,
            "matched_rule": self.matched_rule,
        }

    def __str__(self) -> str:  # pragma: no cover
        marker = "~" if self.changed else "="
        return f"[{marker}] {self.key}  weight={self.weight:.2f}"


def _resolve_weight(
    key: str,
    rules: List[Tuple[str, float]],
    base_weight: float,
) -> Tuple[float, Optional[str]]:
    """Return (weight, matched_pattern) for *key* against *rules*."""
    key_lower = key.lower()
    for pattern, w in rules:
        if fnmatch.fnmatch(key_lower, pattern.lower()):
            return w * base_weight, pattern
    return base_weight, None


def _change_type(diff: KeyDiff) -> str:
    if diff.baseline_value is None:
        return "added"
    if diff.target_value is None:
        return "removed"
    if diff.baseline_value != diff.target_value:
        return "changed"
    return "unchanged"


def weight_diffs(
    diffs: Sequence[KeyDiff],
    rules: Optional[List[Tuple[str, float]]] = None,
    base_weight: float = 1.0,
) -> List[WeightedDiff]:
    """Return *WeightedDiff* instances for every entry in *diffs*."""
    effective_rules = rules if rules is not None else _DEFAULT_RULES
    result: List[WeightedDiff] = []
    for d in diffs:
        ctype = _change_type(d)
        multiplier = _CHANGE_TYPE_MULTIPLIER.get(ctype, 1.0)
        raw_weight, matched = _resolve_weight(d.key, effective_rules, base_weight)
        final_weight = round(raw_weight * multiplier, 4) if multiplier else 0.0
        result.append(
            WeightedDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=ctype != "unchanged",
                weight=final_weight,
                matched_rule=matched if final_weight > 0 else None,
            )
        )
    return result
