"""Key sorting utilities for stack diff output."""
from __future__ import annotations

from enum import Enum
from typing import Dict, Any


class SortOrder(str, Enum):
    ALPHA = "alpha"
    ALPHA_DESC = "alpha_desc"
    CHANGED_FIRST = "changed_first"
    UNCHANGED_FIRST = "unchanged_first"


def sort_keys(
    diff: Dict[str, Any],
    order: SortOrder = SortOrder.ALPHA,
) -> Dict[str, Any]:
    """Return a new dict with keys ordered according to *order*.

    Each value in *diff* is expected to be a dict with at least a
    ``"status"`` key (``"changed"``, ``"added"``, ``"removed"``, or
    ``"unchanged"``).
    """
    if order == SortOrder.ALPHA:
        return dict(sorted(diff.items()))

    if order == SortOrder.ALPHA_DESC:
        return dict(sorted(diff.items(), reverse=True))

    _changed = {"changed", "added", "removed"}

    if order == SortOrder.CHANGED_FIRST:
        return dict(
            sorted(
                diff.items(),
                key=lambda kv: (0 if kv[1].get("status") in _changed else 1, kv[0]),
            )
        )

    if order == SortOrder.UNCHANGED_FIRST:
        return dict(
            sorted(
                diff.items(),
                key=lambda kv: (1 if kv[1].get("status") in _changed else 0, kv[0]),
            )
        )

    return diff  # fallback – unknown order
