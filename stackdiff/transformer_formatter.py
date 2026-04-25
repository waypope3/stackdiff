"""Formatter for TransformedDiff results."""

from __future__ import annotations

from typing import List

from stackdiff.differ_transformer import TransformedDiff

try:
    import colorama
    colorama.init(autoreset=True)
    _YELLOW = colorama.Fore.YELLOW
    _GREEN = colorama.Fore.GREEN
    _RED = colorama.Fore.RED
    _CYAN = colorama.Fore.CYAN
    _RESET = colorama.Style.RESET_ALL
except ImportError:  # pragma: no cover
    _YELLOW = _GREEN = _RED = _CYAN = _RESET = ""


def _c(colour: str, text: str) -> str:
    return f"{colour}{text}{_RESET}"


def format_transformed(diffs: List[TransformedDiff], *, show_original: bool = False) -> str:
    """Render a human-readable table of transformed diffs."""
    if not diffs:
        return "No transformed diffs."
    lines: List[str] = []
    applied = diffs[0].transforms_applied
    lines.append(_c(_CYAN, f"Transforms: {', '.join(applied) if applied else 'none'}"))
    lines.append("")
    for d in diffs:
        marker = _c(_YELLOW, "~") if d.changed else _c(_GREEN, "=")
        lines.append(f"  {marker} {d.key}")
        if show_original and (d.baseline_value != d.transformed_baseline
                               or d.target_value != d.transformed_target):
            lines.append(f"      original  : {d.baseline_value!r} -> {d.target_value!r}")
        lines.append(f"      transformed: {d.transformed_baseline!r} -> {d.transformed_target!r}")
    changed = sum(1 for d in diffs if d.changed)
    lines.append("")
    lines.append(_c(_CYAN, f"Summary: {changed}/{len(diffs)} keys differ after transform"))
    return "\n".join(lines)


def format_transformed_table(diffs: List[TransformedDiff]) -> str:
    """Compact tabular view."""
    if not diffs:
        return "key\tchanged\ttransformed_baseline\ttransformed_target"
    rows = ["key\tchanged\ttransformed_baseline\ttransformed_target"]
    for d in diffs:
        rows.append(f"{d.key}\t{d.changed}\t{d.transformed_baseline}\t{d.transformed_target}")
    return "\n".join(rows)
