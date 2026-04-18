"""Format a MergeResult for terminal or text output."""
from __future__ import annotations
from stackdiff.differ_merger import MergeResult, MergedDiff

_COLOURS = {
    "diverged": "\033[33m",       # yellow
    "new_in_target": "\033[32m",  # green
    "only_in_baseline": "\033[31m", # red
    "same": "\033[0m",
    "reset": "\033[0m",
}

_LABELS = {
    "diverged": "DIVERGED",
    "new_in_target": "NEW",
    "only_in_baseline": "REMOVED",
    "same": "SAME",
}


def _c(text: str, status: str, colour: bool) -> str:
    if not colour:
        return text
    return f"{_COLOURS.get(status, '')}{text}{_COLOURS['reset']}"


def _format_entry(m: MergedDiff, colour: bool) -> str:
    label = _LABELS.get(m.status, m.status)
    coloured_label = _c(f"[{label}]", m.status, colour)
    parts = [f"  {coloured_label} {m.key}"]
    if m.status == "diverged" and m.baseline_diff and m.target_diff:
        parts.append(f"    baseline: {m.baseline_diff.old!r} -> {m.baseline_diff.new!r}")
        parts.append(f"    target:   {m.target_diff.old!r} -> {m.target_diff.new!r}")
    elif m.baseline_diff and m.status != "same":
        parts.append(f"    {m.baseline_diff.old!r} -> {m.baseline_diff.new!r}")
    elif m.target_diff and m.status != "same":
        parts.append(f"    {m.target_diff.old!r} -> {m.target_diff.new!r}")
    return "\n".join(parts)


def format_merge(result: MergeResult, colour: bool = True) -> str:
    if not result.merged:
        return "No keys to compare."
    lines = ["Merge comparison:"]
    for m in result.merged:
        lines.append(_format_entry(m, colour))
    total = len(result.merged)
    diverged = len(result.by_status("diverged"))
    lines.append(f"\nTotal: {total}  Diverged: {diverged}")
    return "\n".join(lines)
