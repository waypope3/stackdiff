"""Text/table formatting for PivotResult."""
from __future__ import annotations

import sys
from typing import Optional

from stackdiff.differ_pivot import PivotResult

_COLOURS = {
    "added": "\033[32m",
    "removed": "\033[31m",
    "changed": "\033[33m",
    "unchanged": "\033[37m",
}
_RESET = "\033[0m"


def _c(label: str, text: str, *, colour: bool) -> str:
    if not colour:
        return text
    code = _COLOURS.get(label, "")
    return f"{code}{text}{_RESET}" if code else text


def format_pivot(result: PivotResult, *, colour: Optional[bool] = None) -> str:
    """Return a human-readable breakdown of the pivot."""
    if colour is None:
        colour = sys.stdout.isatty()

    lines: list[str] = [f"Pivot by: {result.dimension}"]
    lines.append("-" * 40)
    for label, bucket in sorted(result.buckets.items()):
        count = len(bucket.diffs)
        header = _c(label, f"  {label:<20} {count:>4} key(s)", colour=colour)
        lines.append(header)
    lines.append("-" * 40)
    total = sum(len(b.diffs) for b in result.buckets.values())
    lines.append(f"  {'total':<20} {total:>4} key(s)")
    return "\n".join(lines)


def format_pivot_table(result: PivotResult, *, colour: Optional[bool] = None) -> str:
    """Return a compact table listing every key under its bucket."""
    if colour is None:
        colour = sys.stdout.isatty()

    lines: list[str] = [f"Pivot by: {result.dimension}", ""]
    for label, bucket in sorted(result.buckets.items()):
        heading = _c(label, f"[{label}]", colour=colour)
        lines.append(heading)
        for d in bucket.diffs:
            lines.append(f"  {d.key}")
        lines.append("")
    return "\n".join(lines).rstrip()
