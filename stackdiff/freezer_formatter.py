"""Terminal formatter for FrozenDiff results."""
from __future__ import annotations

from typing import List

from stackdiff.differ_freezer import FrozenDiff

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"


def _c(code: str, text: str, *, colour: bool) -> str:
    return f"{code}{text}{_RESET}" if colour else text


def format_frozen(diffs: List[FrozenDiff], *, colour: bool = True) -> str:
    """Return a human-readable block for a list of FrozenDiff entries."""
    lines: List[str] = []
    for d in diffs:
        if d.frozen and not d.changed:
            # frozen + stable: dim
            key_part = _c(_DIM, d.key, colour=colour)
            val_part = _c(_DIM, d.baseline_value, colour=colour)
            lines.append(f"  ❄ {key_part}: {val_part}")
        elif d.frozen and d.changed:
            # frozen but drifted: yellow warning
            key_part = _c(_YELLOW + _BOLD, d.key, colour=colour)
            before = _c(_RED, d.baseline_value, colour=colour)
            after = _c(_GREEN, d.target_value, colour=colour)
            freeze_note = _c(_YELLOW, f"(frozen: {d.freeze_pattern})", colour=colour)
            lines.append(f"  ⚠ {key_part}: {before} → {after}  {freeze_note}")
        elif d.changed:
            key_part = _c(_BOLD, d.key, colour=colour)
            before = _c(_RED, d.baseline_value, colour=colour)
            after = _c(_GREEN, d.target_value, colour=colour)
            lines.append(f"  ~ {key_part}: {before} → {after}")
        else:
            key_part = _c(_DIM, d.key, colour=colour)
            val_part = _c(_DIM, d.baseline_value, colour=colour)
            lines.append(f"  = {key_part}: {val_part}")
    return "\n".join(lines)


def format_frozen_summary(diffs: List[FrozenDiff], *, colour: bool = True) -> str:
    """Return a one-line summary of frozen/drifted counts."""
    total = len(diffs)
    frozen_count = sum(1 for d in diffs if d.frozen)
    drifted = sum(1 for d in diffs if d.frozen and d.changed)
    changed = sum(1 for d in diffs if d.changed)

    parts = [
        f"total={total}",
        _c(_CYAN, f"frozen={frozen_count}", colour=colour),
        _c(_YELLOW, f"drifted={drifted}", colour=colour),
        _c(_RED if changed else _DIM, f"changed={changed}", colour=colour),
    ]
    return "  ".join(parts)
