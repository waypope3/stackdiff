"""Key filtering utilities for stackdiff."""
from __future__ import annotations

import fnmatch
from typing import Dict, List, Optional


def filter_keys(
    stack: Dict[str, str],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Return a copy of *stack* with keys filtered by include/exclude glob patterns.

    Args:
        stack:   Original flat key/value mapping.
        include: If provided, only keys matching at least one pattern are kept.
        exclude: If provided, keys matching any pattern are removed.
                 Exclusion is applied after inclusion.

    Returns:
        Filtered dictionary.
    """
    result = dict(stack)

    if include:
        result = {
            k: v
            for k, v in result.items()
            if any(fnmatch.fnmatch(k, pat) for pat in include)
        }

    if exclude:
        result = {
            k: v
            for k, v in result.items()
            if not any(fnmatch.fnmatch(k, pat) for pat in exclude)
        }

    return result


def apply_filters(
    baseline: Dict[str, str],
    target: Dict[str, str],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> tuple[Dict[str, str], Dict[str, str]]:
    """Apply the same include/exclude filters to both stacks."""
    return (
        filter_keys(baseline, include=include, exclude=exclude),
        filter_keys(target, include=include, exclude=exclude),
    )
