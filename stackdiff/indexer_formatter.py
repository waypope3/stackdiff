"""Format a DiffIndex for terminal or plain-text output."""
from __future__ import annotations

import sys
from typing import List, Optional

from stackdiff.differ_indexer import DiffIndex, IndexedDiff

_COLOURS = {
    "changed": "\033[33m",
    "added": "\033[32m",
    "removed": "\033[31m",
    "unchanged": "\033[90m",
    "reset": "\033[0m",
}


def _c(status: str, text: str, colour: bool) -> str:
    if not colour:
        return text
    code = _COLOURS.get(status, "")
    return f"{code}{text}{_COLOURS['reset']}"


def _marker(status: str) -> str:
    return {"changed": "~", "added": "+", "removed": "-", "unchanged": "="}.get(status, "?")


def format_index_entry(entry: IndexedDiff, colour: bool = True) -> str:
    marker = _marker(entry.status)
    line = f"  {marker} {entry.key}"
    if entry.status == "changed":
        line += f"  [{entry.baseline_value!r} -> {entry.target_value!r}]"
    elif entry.status == "added":
        line += f"  [{entry.target_value!r}]"
    elif entry.status == "removed":
        line += f"  [{entry.baseline_value!r}]"
    return _c(entry.status, line, colour)


def format_index(
    index: DiffIndex,
    statuses: Optional[List[str]] = None,
    colour: bool = True,
) -> str:
    """Render the full index, optionally filtered to specific statuses."""
    entries = index.ordered
    if statuses:
        entries = [e for e in entries if e.status in statuses]

    if not entries:
        return "(no entries)"

    lines = [f"DiffIndex  total={len(index)}  shown={len(entries)}"]
    for entry in entries:
        lines.append(format_index_entry(entry, colour=colour))
    return "\n".join(lines)


def format_index_table(index: DiffIndex, colour: bool = True) -> str:
    """Render a compact table with counts per status."""
    rows = []
    for status in ("changed", "added", "removed", "unchanged"):
        count = len(index.with_status(status))
        label = _c(status, status.capitalize(), colour)
        rows.append(f"  {label:<20} {count}")
    header = "Status               Count"
    sep = "-" * 28
    return "\n".join([header, sep] + rows)
