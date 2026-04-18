"""Truncate long string values in diff output to keep reports readable."""

from __future__ import annotations

DEFAULT_MAX_LENGTH = 120
_ELLIPSIS = "..."


def truncate_value(value: str, max_length: int = DEFAULT_MAX_LENGTH) -> str:
    """Return *value* truncated to *max_length* characters.

    If truncation occurs the string is suffixed with '...' and the total
    returned length equals *max_length*.
    """
    if not isinstance(value, str):
        raise TypeError(f"expected str, got {type(value).__name__}")
    if max_length < len(_ELLIPSIS):
        raise ValueError(f"max_length must be >= {len(_ELLIPSIS)}")
    if len(value) <= max_length:
        return value
    return value[: max_length - len(_ELLIPSIS)] + _ELLIPSIS


def truncate_diff(diff: dict[str, dict], max_length: int = DEFAULT_MAX_LENGTH) -> dict[str, dict]:
    """Return a copy of *diff* with all string values truncated.

    *diff* is expected to be a mapping of key -> {"baseline": ..., "target": ...}
    as produced by :func:`stackdiff.differ.diff_stacks`.
    """
    result: dict[str, dict] = {}
    for key, entry in diff.items():
        new_entry: dict = {}
        for side in ("baseline", "target"):
            if side in entry:
                raw = entry[side]
                new_entry[side] = truncate_value(str(raw), max_length) if raw is not None else raw
        # preserve any extra fields (e.g. "status")
        for k, v in entry.items():
            if k not in ("baseline", "target"):
                new_entry[k] = v
        result[key] = new_entry
    return result
