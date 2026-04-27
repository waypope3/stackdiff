"""Format CorrelatedDiff results for terminal output."""
from __future__ import annotations

from typing import List, Sequence

from stackdiff.differ_correlator import CorrelatedDiff


def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _marker(diff: CorrelatedDiff) -> str:
    if diff.changed:
        return _c(33, "~")
    return _c(32, "=")


def format_correlated(
    diffs: Sequence[CorrelatedDiff],
    show_unchanged: bool = False,
    max_co: int = 3,
) -> str:
    lines: List[str] = []
    changed = [d for d in diffs if d.changed]
    unchanged = [d for d in diffs if not d.changed]

    lines.append(_c(1, f"Correlation report  ({len(changed)} changed, {len(unchanged)} unchanged)"))
    lines.append("")

    for diff in changed:
        marker = _marker(diff)
        co = diff.co_changed_with[:max_co]
        co_str = ", ".join(co) if co else _c(2, "none")
        score_str = _c(36, f"{diff.correlation_score:.2f}")
        lines.append(
            f"  {marker} {_c(1, diff.key)}"
            f"  {diff.baseline_value!r} -> {diff.target_value!r}"
            f"  co-changes: {co_str}  score: {score_str}"
        )

    if show_unchanged:
        lines.append("")
        for diff in unchanged:
            lines.append(f"  {_marker(diff)} {diff.key}")

    return "\n".join(lines)


def format_correlated_table(
    diffs: Sequence[CorrelatedDiff],
    max_co: int = 3,
) -> str:
    header = f"{'KEY':<30} {'SCORE':>6}  CO-CHANGED WITH"
    sep = "-" * 72
    rows = [header, sep]
    for diff in diffs:
        if not diff.changed:
            continue
        co = ", ".join(diff.co_changed_with[:max_co]) or "-"
        rows.append(f"{diff.key:<30} {diff.correlation_score:>6.2f}  {co}")
    if len(rows) == 2:
        rows.append("  (no changed keys)")
    return "\n".join(rows)
