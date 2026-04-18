"""Format a DiffSummary for terminal or report output."""
from __future__ import annotations

from stackdiff.summariser import DiffSummary

_RESET = "\033[0m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


def _c(text: str, code: str, colour: bool) -> str:
    return f"{code}{text}{_RESET}" if colour else text


def format_summary(summary: DiffSummary, *, colour: bool = True) -> str:
    """Return a formatted one-line summary string."""
    if not summary.has_diff:
        msg = f"No differences ({summary.total} key(s) compared)"
        return _c(msg, _GREEN, colour)

    parts = []
    if summary.changed:
        parts.append(_c(f"{summary.changed} changed", _YELLOW, colour))
    if summary.added:
        parts.append(_c(f"{summary.added} added", _GREEN, colour))
    if summary.removed:
        parts.append(_c(f"{summary.removed} removed", _RED, colour))

    total_label = _c(f"{summary.total} key(s)", _BOLD, colour)
    return f"{total_label}: " + ", ".join(parts)


def format_summary_table(summary: DiffSummary) -> str:
    """Return a plain-text table representation of the summary."""
    rows = [
        ("Total", summary.total),
        ("Changed", summary.changed),
        ("Added", summary.added),
        ("Removed", summary.removed),
        ("Unchanged", summary.unchanged),
    ]
    width = max(len(label) for label, _ in rows)
    lines = [f"{label:<{width}}  {value}" for label, value in rows]
    return "\n".join(lines)
