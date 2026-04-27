"""Sentinel-based diff monitoring: flag diffs that cross defined alert thresholds."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import List, Optional, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class SentinelRule:
    """A rule that triggers an alert when matched."""
    pattern: str          # glob pattern matched against the key
    change_types: List[str] = field(default_factory=lambda: ["changed", "added", "removed"])
    message: str = "sentinel rule triggered"

    def matches(self, diff: KeyDiff) -> bool:
        if not fnmatch(diff.key, self.pattern):
            return False
        change_type = _change_type(diff)
        return change_type in self.change_types


def _change_type(diff: KeyDiff) -> str:
    if diff.old_value is None and diff.new_value is not None:
        return "added"
    if diff.old_value is not None and diff.new_value is None:
        return "removed"
    if diff.old_value != diff.new_value:
        return "changed"
    return "unchanged"


@dataclass
class SentinelledDiff:
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    changed: bool
    alerted: bool
    alert_message: Optional[str]
    matched_rule: Optional[str]

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "changed": self.changed,
            "alerted": self.alerted,
            "alert_message": self.alert_message,
            "matched_rule": self.matched_rule,
        }

    def __str__(self) -> str:
        marker = "[ALERT]" if self.alerted else "[ok]"
        return f"{marker} {self.key}: {self.old_value!r} -> {self.new_value!r}"


def sentinel_diffs(
    diffs: Sequence[KeyDiff],
    rules: Sequence[SentinelRule],
) -> List[SentinelledDiff]:
    """Apply sentinel rules to a list of diffs, flagging any that match."""
    result: List[SentinelledDiff] = []
    for diff in diffs:
        changed = diff.old_value != diff.new_value
        alerted = False
        alert_message: Optional[str] = None
        matched_rule: Optional[str] = None
        for rule in rules:
            if rule.matches(diff):
                alerted = True
                alert_message = rule.message
                matched_rule = rule.pattern
                break
        result.append(SentinelledDiff(
            key=diff.key,
            old_value=diff.old_value,
            new_value=diff.new_value,
            changed=changed,
            alerted=alerted,
            alert_message=alert_message,
            matched_rule=matched_rule,
        ))
    return result
