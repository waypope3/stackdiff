"""Format ranked diffs for terminal output."""
from __future__ import annotations

from typing import List

from stackdiff.differ_ranker import RankedDiff, _status

try:
    from colorama import Fore, Style
    _COLOUR = True
except ImportError:  # pragma: no cover
    _COLOUR = False


_STATUS_COLOUR = {
    "removed": "\033[31m",   # red
    "added":   "\033[32m",   # green
    "changed": "\033[33m",   # yellow
    "unchanged": "\033[0m",  # reset
}
_RESET = "\033[0m"


def _c(text: str, status: str, colour: bool) -> str:
    if not colour:
        return text
    return _STATUS_COLOUR.get(status, "") + text + _RESET


def format_ranked(ranked: List[RankedDiff], *, colour: bool = True) -> str:
    """Return a formatted table of ranked diffs."""
    if not ranked:
        return "(no diffs)"

    lines = [f"{'#':<4} {'KEY':<30} {'STATUS':<10} {'BASELINE':<20} TARGET"]
    lines.append("-" * 80)
    for rd in ranked:
        status = _status(rd.diff)
        baseline = str(rd.diff.baseline) if rd.diff.baseline is not None else "—"
        target = str(rd.diff.target) if rd.diff.target is not None else "—"
        row = f"{rd.rank:<4} {rd.key:<30} {status:<10} {baseline:<20} {target}"
        lines.append(_c(row, status, colour))
    return "\n".join(lines)
