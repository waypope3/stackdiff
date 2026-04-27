"""Format TracedDiff objects for terminal output."""
from __future__ import annotations

from typing import List

from stackdiff.differ_tracer import TracedDiff

try:
    from colorama import Fore, Style
    _COLOUR = True
except ImportError:  # pragma: no cover
    _COLOUR = False


def _c(text: str, colour: str) -> str:
    if not _COLOUR:
        return text
    return f"{colour}{text}{Style.RESET_ALL}"


def format_trace(traced: TracedDiff, *, colour: bool = True) -> str:
    """Render a single TracedDiff as a multi-line string."""
    lines: list[str] = []
    marker = _c("~", Fore.YELLOW) if (colour and traced.ever_changed) else "~"
    stable = _c("=", Fore.GREEN) if colour else "="
    header = f"{marker if traced.ever_changed else stable} {traced.key}  "\
             f"(changes: {traced.total_changes}/{len(traced.history)})"
    lines.append(header)
    for entry in traced.history:
        snap = entry.snapshot_id
        if entry.changed:
            bv = entry.baseline_value or "<none>"
            tv = entry.target_value or "<none>"
            if colour:
                bv = _c(bv, Fore.RED)
                tv = _c(tv, Fore.GREEN)
            lines.append(f"  [{snap}]  {bv} -> {tv}")
        else:
            val = entry.target_value or "<none>"
            lines.append(f"  [{snap}]  {val} (unchanged)")
    return "\n".join(lines)


def format_trace_table(traces: List[TracedDiff], *, colour: bool = True) -> str:
    """Render a summary table of all traced keys."""
    if not traces:
        return "No trace data."

    header = f"{'KEY':<40} {'SNAPSHOTS':>9} {'CHANGES':>8}"
    sep = "-" * len(header)
    rows = [header, sep]
    for t in traces:
        key_col = t.key[:39]
        changed_col = str(t.total_changes)
        snap_col = str(len(t.history))
        if colour and t.ever_changed:
            key_col = _c(key_col, Fore.YELLOW)
        rows.append(f"{key_col:<40} {snap_col:>9} {changed_col:>8}")
    rows.append(sep)
    rows.append(f"Total keys traced: {len(traces)}")
    return "\n".join(rows)
