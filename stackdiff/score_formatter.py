"""Format a DiffScore for terminal or plain-text output."""
from __future__ import annotations
import sys
from stackdiff.differ_scorer import DiffScore

_COLOURS = {
    "none": "\033[32m",    # green
    "low": "\033[36m",     # cyan
    "medium": "\033[33m",  # yellow
    "high": "\033[31m",    # red
}
_RESET = "\033[0m"


def _c(text: str, colour: str, *, colour_enabled: bool) -> str:
    if not colour_enabled:
        return text
    return f"{colour}{text}{_RESET}"


def format_score(score: DiffScore, *, colour: bool | None = None) -> str:
    """Return a single-line formatted score string."""
    if colour is None:
        colour = sys.stdout.isatty()
    sev_colour = _COLOURS.get(score.severity, "")
    severity_str = _c(score.severity.upper(), sev_colour, colour_enabled=colour)
    pct = f"{score.score:.1%}"
    return (
        f"Severity: {severity_str}  "
        f"Score: {pct}  "
        f"(changed={score.changed} added={score.added} "
        f"removed={score.removed} total={score.total})"
    )


def format_score_table(score: DiffScore, *, colour: bool | None = None) -> str:
    """Return a multi-line table representation of the score."""
    if colour is None:
        colour = sys.stdout.isatty()
    sev_colour = _COLOURS.get(score.severity, "")
    rows = [
        ("Severity", _c(score.severity.upper(), sev_colour, colour_enabled=colour)),
        ("Score", f"{score.score:.2%}"),
        ("Changed", str(score.changed)),
        ("Added", str(score.added)),
        ("Removed", str(score.removed)),
        ("Unchanged", str(score.total - score.changed - score.added - score.removed)),
        ("Total keys", str(score.total)),
    ]
    width = max(len(r[0]) for r in rows)
    lines = [f"  {label:<{width}}  {value}" for label, value in rows]
    return "\n".join(lines)
