"""Diff logic for comparing two stack output dictionaries."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiffResult:
    added: dict[str, Any] = field(default_factory=dict)
    removed: dict[str, Any] = field(default_factory=dict)
    changed: dict[str, tuple[Any, Any]] = field(default_factory=dict)
    unchanged: dict[str, Any] = field(default_factory=dict)

    @property
    def has_diff(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.changed:
            parts.append(f"~{len(self.changed)} changed")
        if not parts:
            return "No differences found."
        return ", ".join(parts)


def diff_stacks(base: dict[str, Any], target: dict[str, Any]) -> DiffResult:
    """Compare two flat stack output dicts and return a DiffResult."""
    result = DiffResult()
    all_keys = set(base) | set(target)

    for key in all_keys:
        in_base = key in base
        in_target = key in target

        if in_base and not in_target:
            result.removed[key] = base[key]
        elif in_target and not in_base:
            result.added[key] = target[key]
        elif base[key] != target[key]:
            result.changed[key] = (base[key], target[key])
        else:
            result.unchanged[key] = base[key]

    return result
