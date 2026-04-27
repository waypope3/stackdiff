"""Formatter for AnnotatedDiff2 results produced by differ_annotator."""
from __future__ import annotations

from typing import List

from stackdiff.differ_annotator import AnnotatedDiff2

try:
    from colorama import Fore, Style  # type: ignore
    _COLOUR = True
except ImportError:
    _COLOUR = False


def _c(text: str, colour: str) -> str:
    if not _COLOUR:
        return text
    return f"{colour}{text}{Style.RESET_ALL}"


def _marker(diff: AnnotatedDiff2) -> str:
    if diff.baseline_value is None:
        return _c("+", Fore.GREEN if _COLOUR else "+")
    if diff.target_value is None:
        return _c("-", Fore.RED if _COLOUR else "-")
    if diff.changed:
        return _c("~", Fore.YELLOW if _COLOUR else "~")
    return _c("=", Fore.WHITE if _COLOUR else "=")


def format_annotated2(diffs: List[AnnotatedDiff2], show_unchanged: bool = False) -> str:
    """Return a multi-line formatted string for a list of AnnotatedDiff2."""
    lines: List[str] = []
    shown = [d for d in diffs if show_unchanged or d.changed]
    for d in shown:
        marker = _marker(d)
        tags: List[str] = []
        if d.domain:
            tags.append(d.domain)
        if d.value_hint:
            tags.append(d.value_hint)
        tag_str = f"  [{', '.join(tags)}]" if tags else ""
        base = d.baseline_value if d.baseline_value is not None else "<none>"
        tgt = d.target_value if d.target_value is not None else "<none>"
        lines.append(f"{marker} {d.key}{tag_str}")
        lines.append(f"    baseline : {base}")
        lines.append(f"    target   : {tgt}")
    total = len(diffs)
    changed = sum(1 for d in diffs if d.changed)
    lines.append(f"\n{changed}/{total} keys changed")
    return "\n".join(lines)


def format_annotated2_table(diffs: List[AnnotatedDiff2]) -> str:
    """Return a compact table of annotated diffs."""
    header = f"{'KEY':<30} {'DOMAIN':<12} {'HINT':<8} {'STATUS'}"
    sep = "-" * len(header)
    rows = [header, sep]
    for d in diffs:
        status = ", ".join(d.notes) if d.notes else "unchanged"
        domain = d.domain or ""
        hint = d.value_hint or ""
        rows.append(f"{d.key:<30} {domain:<12} {hint:<8} {status}")
    return "\n".join(rows)
