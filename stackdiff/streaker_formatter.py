"""Formatter for StreakedDiff results."""
from __future__ import annotations

from typing import List, Sequence

from stackdiff.differ_streaker import StreakedDiff

try:
    import colorama  # type: ignore
    colorama.init(autoreset=True)
    _RED = colorama.Fore.RED
    _GREEN = colorama.Fore.GREEN
    _YELLOW = colorama.Fore.YELLOW
    _RESET = colorama.Style.RESET_ALL
except ImportError:  # pragma: no cover
    _RED = _GREEN = _YELLOW = _RESET = ""


def _c(colour: str, text: str) -> str:
    return f"{colour}{text}{_RESET}" if colour else text


def format_streaked(diffs: Sequence[StreakedDiff]) -> str:
    """Return a human-readable string summarising streaked diffs."""
    if not diffs:
        return "No diffs to display."

    lines: List[str] = []
    for d in diffs:
        if d.changed:
            streak_tag = f" (streak: {d.streak})" if d.streak > 1 else ""
            always_tag = _c(_RED, " [ALWAYS CHANGED]") if d.always_changed else ""
            line = _c(_YELLOW, f"~ {d.key}") + f": {d.baseline_value!r} -> {d.target_value!r}{streak_tag}{always_tag}"
        else:
            line = _c(_GREEN, f"= {d.key}") + f": {d.baseline_value!r}"
        lines.append(line)

    changed = sum(1 for d in diffs if d.changed)
    always = sum(1 for d in diffs if d.always_changed)
    lines.append("")
    lines.append(f"Total: {len(diffs)}  Changed: {changed}  Always-changed: {always}")
    return "\n".join(lines)


def format_streaked_table(diffs: Sequence[StreakedDiff]) -> str:
    """Return a fixed-width table of streaked diffs."""
    if not diffs:
        return "No diffs to display."

    col_key = max(len(d.key) for d in diffs)
    header = f"{'KEY':<{col_key}}  {'CHANGED':<8}  {'STREAK':<7}  ALWAYS"
    sep = "-" * len(header)
    lines = [header, sep]
    for d in diffs:
        changed_str = _c(_YELLOW, "yes") if d.changed else _c(_GREEN, "no")
        always_str = _c(_RED, "yes") if d.always_changed else "no"
        lines.append(f"{d.key:<{col_key}}  {changed_str:<8}  {d.streak:<7}  {always_str}")
    return "\n".join(lines)
