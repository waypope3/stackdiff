"""Format WeightedDiff results for terminal and table output."""
from __future__ import annotations

from typing import List

from stackdiff.differ_weighter import WeightedDiff

try:
    import colorama  # type: ignore
    colorama.init(autoreset=True)
    _RED = colorama.Fore.RED
    _GREEN = colorama.Fore.GREEN
    _YELLOW = colorama.Fore.YELLOW
    _CYAN = colorama.Fore.CYAN
    _RESET = colorama.Style.RESET_ALL
except ImportError:  # pragma: no cover
    _RED = _GREEN = _YELLOW = _CYAN = _RESET = ""


def _c(text: str, colour: str) -> str:
    return f"{colour}{text}{_RESET}" if colour else text


def _weight_bar(weight: float, max_weight: float, width: int = 10) -> str:
    if max_weight == 0:
        filled = 0
    else:
        filled = round((weight / max_weight) * width)
    return "█" * filled + "░" * (width - filled)


def format_weighted(diffs: List[WeightedDiff], *, show_bar: bool = True) -> str:
    if not diffs:
        return "No diffs to display."

    max_weight = max((d.weight for d in diffs), default=1.0) or 1.0
    lines: List[str] = []
    for d in sorted(diffs, key=lambda x: x.weight, reverse=True):
        if d.changed:
            colour = _RED if d.target_value is None else (_GREEN if d.baseline_value is None else _YELLOW)
        else:
            colour = ""
        marker = _c("~", colour) if d.changed else "="
        bar = f"  [{_weight_bar(d.weight, max_weight)}]" if show_bar else ""
        rule_note = f"  (rule: {d.matched_rule})" if d.matched_rule else ""
        lines.append(
            f"  {marker} {_c(d.key, colour):<40}  w={d.weight:>6.3f}{bar}{rule_note}"
        )
    return "\n".join(lines)


def format_weighted_table(diffs: List[WeightedDiff]) -> str:
    if not diffs:
        return "No diffs."

    header = f"  {'KEY':<38}  {'WEIGHT':>8}  {'CHANGED':>8}  RULE"
    sep = "  " + "-" * 70
    rows = [header, sep]
    for d in sorted(diffs, key=lambda x: x.weight, reverse=True):
        changed_str = _c("yes", _YELLOW) if d.changed else "no"
        rule_str = d.matched_rule or ""
        rows.append(
            f"  {d.key:<38}  {d.weight:>8.3f}  {changed_str:>8}  {rule_str}"
        )
    rows.append(sep)
    total_weight = sum(d.weight for d in diffs)
    rows.append(f"  {'TOTAL':<38}  {total_weight:>8.3f}")
    return "\n".join(rows)
