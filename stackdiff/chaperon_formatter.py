"""Formatter for ChaperondDiff results."""
from __future__ import annotations

from typing import List, Sequence

from stackdiff.differ_chaperon import ChaperondDiff

try:
    from colorama import Fore, Style  # type: ignore
    _COLOUR = True
except ImportError:  # pragma: no cover
    _COLOUR = False


def _c(text: str, colour: str) -> str:
    if not _COLOUR:
        return text
    return f"{colour}{text}{Style.RESET_ALL}"


def _marker(d: ChaperondDiff) -> str:
    if d.baseline_value is None:
        return _c("+", Fore.GREEN if _COLOUR else "+")
    if d.target_value is None:
        return _c("-", Fore.RED if _COLOUR else "-")
    if d.changed:
        return _c("~", Fore.YELLOW if _COLOUR else "~")
    return _c("=", Fore.CYAN if _COLOUR else "=")


def format_chaperoned(diffs: Sequence[ChaperondDiff], *, show_unchanged: bool = False) -> str:
    lines: List[str] = []
    changed = [d for d in diffs if d.changed]
    unchanged = [d for d in diffs if not d.changed]

    for d in changed:
        companion_note = ""
        if d.companion_key:
            pct = int(d.companion_similarity * 100)
            companion_note = f"  ↔ {d.companion_key} ({pct}% similar)"
        lines.append(f"  {_marker(d)} {d.key}")
        lines.append(f"      baseline : {d.baseline_value!r}")
        lines.append(f"      target   : {d.target_value!r}")
        if companion_note:
            lines.append(f"     {companion_note}")

    if show_unchanged:
        for d in unchanged:
            lines.append(f"  {_marker(d)} {d.key}")

    total = len(diffs)
    n_changed = len(changed)
    lines.append("")
    lines.append(f"  {n_changed}/{total} keys changed")
    return "\n".join(lines)


def format_chaperoned_table(diffs: Sequence[ChaperondDiff]) -> str:
    header = f"  {'KEY':<35} {'ST':<3} {'COMPANION':<35} {'SIM':>5}"
    sep = "  " + "-" * (len(header) - 2)
    rows = [header, sep]
    for d in diffs:
        st = _marker(d)
        comp = d.companion_key or ""
        sim = f"{d.companion_similarity:.0%}" if d.companion_key else ""
        rows.append(f"  {d.key:<35} {st:<3} {comp:<35} {sim:>5}")
    return "\n".join(rows)
