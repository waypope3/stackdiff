"""Formatter for ThresholdedDiff results."""
from __future__ import annotations

from typing import Sequence

from stackdiff.differ_threshold import ThresholdedDiff

try:
    import colorama  # type: ignore
    _RESET = colorama.Style.RESET_ALL
    _RED = colorama.Fore.RED
    _GREEN = colorama.Fore.GREEN
    _YELLOW = colorama.Fore.YELLOW
    _DIM = colorama.Style.DIM
except ImportError:  # pragma: no cover
    _RESET = _RED = _GREEN = _YELLOW = _DIM = ""


def _c(text: str, colour: str) -> str:
    if not colour:
        return text
    return f"{colour}{text}{_RESET}"


def format_thresholded(diffs: Sequence[ThresholdedDiff], *, show_suppressed: bool = False) -> str:
    """Return a human-readable table of thresholded diffs."""
    lines: list[str] = []
    header = f"{'KEY':<40} {'BASELINE':<30} {'TARGET':<30} {'DIST':>4}  STATUS"
    lines.append(header)
    lines.append("-" * len(header))

    for d in diffs:
        if d.suppressed and not show_suppressed:
            continue

        bv = d.baseline_value or ""
        tv = d.target_value or ""

        if d.suppressed:
            status = _c("suppressed", _DIM)
        elif not d.changed:
            status = _c("unchanged", _DIM)
        elif d.baseline_value is None:
            status = _c("added", _GREEN)
        elif d.target_value is None:
            status = _c("removed", _RED)
        else:
            status = _c("changed", _YELLOW)

        dist_str = str(d.edit_distance) if d.changed else "-"
        lines.append(
            f"{d.key:<40} {bv[:30]:<30} {tv[:30]:<30} {dist_str:>4}  {status}"
        )

    visible = [d for d in diffs if not d.suppressed or show_suppressed]
    if not visible:
        lines.append("(no diffs to display)")

    suppressed_count = sum(1 for d in diffs if d.suppressed)
    if suppressed_count and not show_suppressed:
        lines.append(_c(f"\n{suppressed_count} diff(s) suppressed by threshold.", _DIM))

    return "\n".join(lines)
