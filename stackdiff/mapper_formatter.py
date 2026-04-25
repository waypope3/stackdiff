"""Terminal and plain-text formatting for MappedDiff results."""
from __future__ import annotations

from typing import List

from stackdiff.differ_mapper import MappedDiff

try:
    from colorama import Fore, Style  # type: ignore

    _COLOUR = True
except ImportError:  # pragma: no cover
    _COLOUR = False


def _c(text: str, colour: str) -> str:
    if _COLOUR:
        return f"{colour}{text}{Style.RESET_ALL}"
    return text


def format_mapped(diffs: List[MappedDiff], *, colour: bool = True) -> str:
    """Return a human-readable multi-line string for a list of MappedDiff."""
    lines: List[str] = []
    for d in diffs:
        if d.changed:
            if d.baseline_value is None:
                marker = _c("+", Fore.GREEN if colour and _COLOUR else "")
            elif d.target_value is None:
                marker = _c("-", Fore.RED if colour and _COLOUR else "")
            else:
                marker = _c("~", Fore.YELLOW if colour and _COLOUR else "")
        else:
            marker = " "

        label = d.mapped_key
        if d.was_remapped:
            remap_note = _c(f" (mapped from '{d.original_key}')", Fore.CYAN if colour and _COLOUR else "")
        else:
            remap_note = ""

        lines.append(
            f"  [{marker}] {label}{remap_note}: {d.baseline_value!r} -> {d.target_value!r}"
        )
    return "\n".join(lines)


def format_mapped_table(diffs: List[MappedDiff]) -> str:
    """Return a plain-text table suitable for piping or file output."""
    header = f"{'KEY':<30} {'ORIGINAL':<30} {'BASELINE':<20} {'TARGET':<20} CHANGED"
    separator = "-" * len(header)
    rows = [header, separator]
    for d in diffs:
        rows.append(
            f"{d.mapped_key:<30} {d.original_key:<30} "
            f"{str(d.baseline_value):<20} {str(d.target_value):<20} {d.changed}"
        )
    return "\n".join(rows)
