"""Format LabeledDiff lists for terminal output."""
from __future__ import annotations
from typing import List
from stackdiff.differ_labeler import LabeledDiff

try:
    import colorama
    colorama.init(autoreset=True)
    _COLORS = {
        "changed": colorama.Fore.YELLOW,
        "added": colorama.Fore.GREEN,
        "removed": colorama.Fore.RED,
        "unchanged": colorama.Fore.WHITE,
        "reset": colorama.Style.RESET_ALL,
    }
except ImportError:
    _COLORS = {k: "" for k in ("changed", "added", "removed", "unchanged", "reset")}


def _c(text: str, status: str) -> str:
    return f"{_COLORS.get(status, '')}{text}{_COLORS['reset']}"


def format_labeled(diffs: List[LabeledDiff], show_hints: bool = False) -> str:
    if not diffs:
        return "No differences."
    lines = []
    for d in diffs:
        tag = _c(f"[{d.label}]", d.status)
        if d.status == "changed":
            line = f"{tag} {d.key}: {d.baseline_value!r} -> {d.target_value!r}"
        elif d.status == "added":
            line = f"{tag} {d.key}: {d.target_value!r}"
        elif d.status == "removed":
            line = f"{tag} {d.key}: {d.baseline_value!r}"
        else:
            line = f"{tag} {d.key}: {d.target_value!r}"
        if show_hints and d.hint:
            line += f"  # {d.hint}"
        lines.append(line)
    return "\n".join(lines)


def format_labeled_table(diffs: List[LabeledDiff]) -> str:
    if not diffs:
        return "No differences."
    header = f"{'KEY':<30} {'STATUS':<12} {'BASELINE':<20} {'TARGET':<20}"
    sep = "-" * len(header)
    rows = [header, sep]
    for d in diffs:
        bv = str(d.baseline_value) if d.baseline_value is not None else ""
        tv = str(d.target_value) if d.target_value is not None else ""
        row = f"{d.key:<30} {_c(d.label, d.status):<12} {bv:<20} {tv:<20}"
        rows.append(row)
    return "\n".join(rows)
