"""Formatter for SentinelledDiff output."""
from __future__ import annotations

from typing import List, Sequence

from stackdiff.differ_sentinel import SentinelledDiff

try:
    import colorama
    colorama.init(autoreset=True)
    _RED = colorama.Fore.RED
    _YELLOW = colorama.Fore.YELLOW
    _GREEN = colorama.Fore.GREEN
    _RESET = colorama.Style.RESET_ALL
except ImportError:  # pragma: no cover
    _RED = _YELLOW = _GREEN = _RESET = ""


def _c(colour: str, text: str) -> str:
    return f"{colour}{text}{_RESET}" if colour else text


def _marker(diff: SentinelledDiff) -> str:
    if diff.alerted:
        return _c(_RED, "[ALERT]")
    if diff.changed:
        return _c(_YELLOW, "[~]")
    return _c(_GREEN, "[=]")


def format_sentinel(diffs: Sequence[SentinelledDiff], show_unchanged: bool = False) -> str:
    """Return a human-readable sentinel report."""
    lines: List[str] = []
    alerted = [d for d in diffs if d.alerted]
    changed = [d for d in diffs if d.changed and not d.alerted]
    unchanged = [d for d in diffs if not d.changed]

    lines.append(f"Sentinel report — {len(diffs)} keys, {len(alerted)} alert(s)")
    lines.append("")

    for diff in alerted:
        lines.append(f"  {_marker(diff)} {diff.key}")
        lines.append(f"       was : {diff.old_value!r}")
        lines.append(f"       now : {diff.new_value!r}")
        lines.append(f"       rule: {diff.matched_rule}  — {diff.alert_message}")

    for diff in changed:
        lines.append(f"  {_marker(diff)} {diff.key}: {diff.old_value!r} -> {diff.new_value!r}")

    if show_unchanged:
        for diff in unchanged:
            lines.append(f"  {_marker(diff)} {diff.key}: {diff.old_value!r}")

    return "\n".join(lines)


def format_sentinel_table(diffs: Sequence[SentinelledDiff]) -> str:
    """Return a compact table of alerted diffs only."""
    alerted = [d for d in diffs if d.alerted]
    if not alerted:
        return "No sentinel alerts."
    col = max(len(d.key) for d in alerted)
    header = f"  {'KEY':<{col}}  RULE                 MESSAGE"
    sep = "  " + "-" * (col + 40)
    rows = [header, sep]
    for diff in alerted:
        rule = (diff.matched_rule or "")[:20]
        msg = (diff.alert_message or "")[:30]
        rows.append(f"  {_c(_RED, diff.key):<{col + len(_RED) + len(_RESET)}}  {rule:<20} {msg}")
    return "\n".join(rows)
