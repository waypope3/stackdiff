"""Map diff keys through a user-supplied key-translation table.

Allows renaming output keys before display or export without mutating
the underlying diff data.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class MappedDiff:
    """A KeyDiff with an optional display alias applied via a mapping table."""

    original_key: str
    mapped_key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    was_remapped: bool

    def as_dict(self) -> Dict:
        return {
            "original_key": self.original_key,
            "mapped_key": self.mapped_key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "was_remapped": self.was_remapped,
        }

    def __str__(self) -> str:  # pragma: no cover
        marker = "~" if self.changed else "="
        label = f"{self.mapped_key}" + (f" (was: {self.original_key})" if self.was_remapped else "")
        return f"[{marker}] {label}: {self.baseline_value!r} -> {self.target_value!r}"


def map_diffs(
    diffs: Sequence[KeyDiff],
    mapping: Dict[str, str],
) -> List[MappedDiff]:
    """Return *MappedDiff* instances for each entry in *diffs*.

    Parameters
    ----------
    diffs:
        Sequence of raw :class:`~stackdiff.differ.KeyDiff` objects.
    mapping:
        Dictionary mapping original key names to desired display names.
        Keys absent from the mapping are left unchanged.
    """
    result: List[MappedDiff] = []
    for d in diffs:
        mapped_key = mapping.get(d.key, d.key)
        was_remapped = mapped_key != d.key
        changed = d.baseline_value != d.target_value
        result.append(
            MappedDiff(
                original_key=d.key,
                mapped_key=mapped_key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=changed,
                was_remapped=was_remapped,
            )
        )
    return result
