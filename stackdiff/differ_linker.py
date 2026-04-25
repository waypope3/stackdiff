"""Link diff keys across multiple stacks to detect cross-stack dependency changes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.differ import KeyDiff


@dataclass
class LinkedDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    linked_stacks: List[str] = field(default_factory=list)
    is_cross_stack_ref: bool = False

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "linked_stacks": self.linked_stacks,
            "is_cross_stack_ref": self.is_cross_stack_ref,
        }

    def __str__(self) -> str:
        marker = "~" if self.changed else "="
        ref = " [cross-stack]" if self.is_cross_stack_ref else ""
        links = f" (linked: {', '.join(self.linked_stacks)})" if self.linked_stacks else ""
        return f"{marker} {self.key}: {self.baseline_value!r} -> {self.target_value!r}{ref}{links}"


def _is_cross_stack_ref(value: Optional[str]) -> bool:
    """Heuristic: treat values that look like CloudFormation exports or ARNs as cross-stack refs."""
    if not isinstance(value, str):
        return False
    return value.startswith("arn:") or "::" in value or value.startswith("Fn::ImportValue")


def _find_linked_stacks(
    key: str,
    value: Optional[str],
    all_stacks: Dict[str, Dict[str, str]],
    current_stack: str,
) -> List[str]:
    """Return names of stacks (other than current) that reference the same key or value."""
    linked: List[str] = []
    for stack_name, outputs in all_stacks.items():
        if stack_name == current_stack:
            continue
        if key in outputs or (value and value in outputs.values()):
            linked.append(stack_name)
    return linked


def link_diffs(
    diffs: List[KeyDiff],
    all_stacks: Dict[str, Dict[str, str]],
    current_stack: str = "current",
) -> List[LinkedDiff]:
    """Enrich a list of KeyDiff entries with cross-stack linkage information."""
    result: List[LinkedDiff] = []
    for d in diffs:
        linked = _find_linked_stacks(d.key, d.baseline_value or d.target_value, all_stacks, current_stack)
        is_ref = _is_cross_stack_ref(d.baseline_value) or _is_cross_stack_ref(d.target_value)
        result.append(
            LinkedDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=d.baseline_value != d.target_value,
                linked_stacks=linked,
                is_cross_stack_ref=is_ref,
            )
        )
    return result
