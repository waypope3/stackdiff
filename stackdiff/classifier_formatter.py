"""Format classified diffs for terminal output."""
from __future__ import annotations
from typing import Dict, List
from stackdiff.differ_classifier import ClassifiedDiff, group_by_category

try:
    from colorama import Fore, Style
    _COLOUR = True
except ImportError:
    _COLOUR = False

_CAT_COLOURS = {
    "network": "\033[34m",
    "compute": "\033[33m",
    "storage": "\033[35m",
    "database": "\033[36m",
    "iam": "\033[31m",
    "general": "\033[37m",
}
_RESET = "\033[0m"


def _c(text: str, colour: str) -> str:
    return f"{colour}{text}{_RESET}"


def format_classified(classified: List[ClassifiedDiff], *, colour: bool = True) -> str:
    grouped = group_by_category(classified)
    lines: List[str] = []
    for category, items in sorted(grouped.items()):
        changed = [i for i in items if i.changed]
        cat_label = category.upper()
        if colour:
            cat_label = _c(cat_label, _CAT_COLOURS.get(category, _RESET))
        lines.append(f"[{cat_label}] ({len(changed)} changed / {len(items)} total)")
        for item in items:
            marker = "~" if item.changed else " "
            lines.append(f"  {marker} {item.key}: {item.baseline!r} -> {item.current!r}")
    return "\n".join(lines)


def format_classified_table(classified: List[ClassifiedDiff]) -> str:
    header = f"{'KEY':<30} {'CATEGORY':<12} {'CHANGED'}"
    sep = "-" * len(header)
    rows = [header, sep]
    for item in sorted(classified, key=lambda x: (x.category, x.key)):
        rows.append(f"{item.key:<30} {item.category:<12} {'yes' if item.changed else 'no'}")
    return "\n".join(rows)
