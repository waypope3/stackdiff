"""Apply value transformation functions to diff entries before comparison or display."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from stackdiff.differ import KeyDiff

# Built-in named transforms
_STRIP_WHITESPACE: Callable[[str], str] = str.strip
_LOWERCASE: Callable[[str], str] = str.lower
_UPPERCASE: Callable[[str], str] = str.upper
_REMOVE_HYPHENS: Callable[[str], str] = lambda v: v.replace("-", "")
_REMOVE_WHITESPACE: Callable[[str], str] = lambda v: re.sub(r"\s+", "", v)

BUILTIN_TRANSFORMS: Dict[str, Callable[[str], str]] = {
    "strip": _STRIP_WHITESPACE,
    "lower": _LOWERCASE,
    "upper": _UPPERCASE,
    "remove_hyphens": _REMOVE_HYPHENS,
    "remove_whitespace": _REMOVE_WHITESPACE,
}


@dataclass
class TransformedDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    transformed_baseline: Optional[str]
    transformed_target: Optional[str]
    changed: bool
    transforms_applied: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "transformed_baseline": self.transformed_baseline,
            "transformed_target": self.transformed_target,
            "changed": self.changed,
            "transforms_applied": self.transforms_applied,
        }


def _apply_chain(value: Optional[str], transforms: List[Callable[[str], str]]) -> Optional[str]:
    if value is None:
        return None
    result = value
    for fn in transforms:
        result = fn(result)
    return result


def transform_diffs(
    diffs: List[KeyDiff],
    transforms: List[str],
    extra: Optional[Dict[str, Callable[[str], str]]] = None,
) -> List[TransformedDiff]:
    """Return TransformedDiff list with named transforms applied to both sides."""
    registry = {**BUILTIN_TRANSFORMS, **(extra or {})}
    unknown = [t for t in transforms if t not in registry]
    if unknown:
        raise ValueError(f"Unknown transforms: {unknown}")
    fns = [registry[t] for t in transforms]
    result = []
    for d in diffs:
        tb = _apply_chain(d.baseline_value, fns)
        tt = _apply_chain(d.target_value, fns)
        result.append(
            TransformedDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                transformed_baseline=tb,
                transformed_target=tt,
                changed=tb != tt,
                transforms_applied=list(transforms),
            )
        )
    return result
