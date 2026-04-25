"""differ_dispatcher: route diffs to named handlers based on key patterns."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from stackdiff.differ import KeyDiff


@dataclass
class DispatchedDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    handler_name: Optional[str]
    handler_result: Optional[str]

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "handler_name": self.handler_name,
            "handler_result": self.handler_result,
        }

    def __str__(self) -> str:
        marker = "~" if self.changed else "="
        handler_note = f" [{self.handler_name}]" if self.handler_name else ""
        result_note = f" -> {self.handler_result}" if self.handler_result else ""
        return f"{marker} {self.key}{handler_note}{result_note}"


Handler = Callable[[KeyDiff], Optional[str]]


@dataclass
class DispatchRule:
    pattern: str
    handler_name: str
    handler: Handler


def _first_matching_rule(
    key: str, rules: List[DispatchRule]
) -> Optional[DispatchRule]:
    for rule in rules:
        if fnmatch.fnmatch(key, rule.pattern):
            return rule
    return None


def dispatch_diffs(
    diffs: List[KeyDiff],
    rules: List[DispatchRule],
) -> List[DispatchedDiff]:
    """Apply the first matching dispatch rule to each diff.

    If no rule matches, *handler_name* and *handler_result* are ``None``.
    """
    result: List[DispatchedDiff] = []
    for d in diffs:
        changed = d.baseline_value != d.target_value
        rule = _first_matching_rule(d.key, rules)
        if rule is not None:
            handler_result = rule.handler(d)
            handler_name: Optional[str] = rule.handler_name
        else:
            handler_result = None
            handler_name = None
        result.append(
            DispatchedDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=changed,
                handler_name=handler_name,
                handler_result=handler_result,
            )
        )
    return result
