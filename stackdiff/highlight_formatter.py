"""Format highlighted diffs for terminal or plain-text output."""
from __future__ import annotations

from typing import List

from stackdiff.differ_highlighter import HighlightedDiff

_RESET = "\033[0m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_DIM = "\033[2m"


def _c(text: str, code: str, colour: bool) -> str:
    return f"{code}{text}{_RESET}" if colour else text


def format_highlighted(
    diffs: List[HighlightedDiff],
    colour: bool = True,
    show_unchanged: bool = False,
) -> str:
    """Render highlighted diffs as a human-readable string."""
    lines: List[str] = []
    for d in diffs:
        if not d.changed and not show_unchanged:
            continue
        key_label = _c(d.key, _CYAN, colour)
        if d.changed:
            marker = _c("~", _YELLOW, colour)
            lines.append(f"  {marker} {key_label}")
            lines.append(f"      - {d.baseline_highlighted}")
            lines.append(f"      + {d.target_highlighted}")
        else:
            marker = _c("=", _DIM, colour)
            lines.append(f"  {marker} {key_label}: {_c(d.baseline_highlighted, _DIM, colour)}")
    return "\n".join(lines)


def format_highlighted_table(
    diffs: List[HighlightedDiff],
    colour: bool = True,
    show_unchanged: bool = False,
) -> str:
    """Render highlighted diffs as a fixed-width table."""
    visible = [d for d in diffs if d.changed or show_unchanged]
    if not visible:
        return "(no differences)"

    # Strip ANSI for width calculation
    import re
    _ansi_re = re.compile(r"\033\[[0-9;]*m")

    def plain(s: str) -> str:
        return _ansi_re.sub("", s)

    key_w = max(len(plain(d.key)) for d in visible)
    header = f"  {'KEY':<{key_w}}  BASELINE → TARGET"
    sep = "  " + "-" * (key_w + 30)
    rows = [header, sep]
    for d in visible:
        key_label = _c(f"{plain(d.key):<{key_w}}", _CYAN, colour)
        if d.changed:
            rows.append(f"  {key_label}  {d.baseline_highlighted} → {d.target_highlighted}")
        else:
            rows.append(f"  {key_label}  {_c(plain(d.baseline_highlighted), _DIM, colour)}")
    return "\n".join(rows)
