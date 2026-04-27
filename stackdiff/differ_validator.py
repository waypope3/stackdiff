"""Validate diffs against a set of rules, flagging violations."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class ValidationRule:
    """A single validation rule applied to diffs."""
    name: str
    key_pattern: str          # glob pattern matched against diff key
    disallow_changed: bool = False
    disallow_added: bool = False
    disallow_removed: bool = False
    message: Optional[str] = None


@dataclass
class ValidatedDiff:
    """A diff entry decorated with any validation violations."""
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    violations: List[str] = field(default_factory=list)

    @property
    def has_violation(self) -> bool:
        return bool(self.violations)

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "violations": self.violations,
        }

    def __str__(self) -> str:  # pragma: no cover
        flag = "[VIOLATION]" if self.has_violation else "[ok]"
        return f"{flag} {self.key}: {self.baseline_value!r} -> {self.target_value!r}"


def _is_added(d: KeyDiff) -> bool:
    return d.baseline_value is None and d.target_value is not None


def _is_removed(d: KeyDiff) -> bool:
    return d.baseline_value is not None and d.target_value is None


def _is_changed(d: KeyDiff) -> bool:
    return (
        d.baseline_value is not None
        and d.target_value is not None
        and d.baseline_value != d.target_value
    )


def _check_rules(diff: KeyDiff, rules: Sequence[ValidationRule]) -> List[str]:
    violations: List[str] = []
    for rule in rules:
        if not fnmatch.fnmatch(diff.key, rule.key_pattern):
            continue
        msg = rule.message or f"rule '{rule.name}' violated on key '{diff.key}'"
        if rule.disallow_changed and _is_changed(diff):
            violations.append(msg)
        if rule.disallow_added and _is_added(diff):
            violations.append(msg)
        if rule.disallow_removed and _is_removed(diff):
            violations.append(msg)
    return violations


def validate_diffs(
    diffs: Sequence[KeyDiff],
    rules: Sequence[ValidationRule],
) -> List[ValidatedDiff]:
    """Return ValidatedDiff instances, each annotated with any rule violations."""
    result: List[ValidatedDiff] = []
    for d in diffs:
        changed = d.baseline_value != d.target_value
        violations = _check_rules(d, rules)
        result.append(
            ValidatedDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=changed,
                violations=violations,
            )
        )
    return result


def filter_violations(validated: Sequence[ValidatedDiff]) -> List[ValidatedDiff]:
    """Return only the ValidatedDiff entries that have at least one violation."""
    return [v for v in validated if v.has_violation]
