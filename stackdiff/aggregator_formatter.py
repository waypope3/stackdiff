"""Format aggregated diff results for terminal and table output."""
from __future__ import annotations

from typing import List

from stackdiff.differ_aggregator import AggregatedDiff

try:
    from colorama import Fore, Style
    _COLOUR = True
except ImportError:  # pragma: no cover
    _COLOUR = False


def _c(text: str, colour: str) -> str:
    if not _COLOUR:
        return text
    return f"{colour}{text}{Style.RESET_ALL}"


def format_aggregated(diffs: List[AggregatedDiff], *, colour: bool = True) -> str:
    """Return a human-readable multi-line string for terminal output."""
    if not diffs:
        return "No keys to display."

    lines: List[str] = []
    sources = diffs[0].sources
    header = f"{'KEY':<40}" + "".join(f"{s:<25}" for s in sources) + "  STATUS"
    lines.append(header)
    lines.append("-" * len(header))

    for d in diffs:
        key_col = d.key[:38].ljust(40)
        val_cols = "".join(
            (str(v) if v is not None else "<missing>")[:23].ljust(25)
            for v in d.values.values()
        )
        if d.is_consistent:
            status = _c("OK", Fore.GREEN) if colour and _COLOUR else "OK"
        else:
            status = _c("DIVERGED", Fore.RED) if colour and _COLOUR else "DIVERGED"
        lines.append(f"{key_col}{val_cols}  {status}")

    return "\n".join(lines)


def format_aggregated_table(diffs: List[AggregatedDiff]) -> str:
    """Return a Markdown table of aggregated diffs."""
    if not diffs:
        return "_No data._"

    sources = diffs[0].sources
    header_cols = ["Key"] + sources + ["Consistent"]
    header = "| " + " | ".join(header_cols) + " |"
    separator = "| " + " | ".join("---" for _ in header_cols) + " |"

    rows = [header, separator]
    for d in diffs:
        vals = [str(v) if v is not None else "_missing_" for v in d.values.values()]
        consistent = "✓" if d.is_consistent else "✗"
        row = "| " + " | ".join([d.key] + vals + [consistent]) + " |"
        rows.append(row)

    return "\n".join(rows)
