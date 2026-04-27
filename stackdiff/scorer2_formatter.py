"""Formatter for ExtendedScore produced by differ_scorer2."""
from __future__ import annotations

from stackdiff.differ_scorer2 import ExtendedScore, WeightedScore

try:
    from colorama import Fore, Style
    _COLOUR = True
except ImportError:
    _COLOUR = False


def _c(text: str, colour: str) -> str:
    if not _COLOUR:
        return text
    return f"{colour}{text}{Style.RESET_ALL}"


def _marker(entry: WeightedScore) -> str:
    if entry.changed:
        return _c("~", Fore.YELLOW)
    return _c("=", Fore.GREEN)


def format_extended_score(score: ExtendedScore, *, show_unchanged: bool = False) -> str:
    """Return a human-readable multi-line report for an ExtendedScore."""
    lines: list[str] = []
    for entry in score.entries:
        if not show_unchanged and not entry.changed:
            continue
        marker = _marker(entry)
        lines.append(
            f"  {marker} {entry.key:<40} "
            f"domain={entry.domain:<10} "
            f"weight={entry.weight:.1f}  "
            f"impact={entry.weighted_impact:.1f}"
        )

    pct = score.impact_ratio * 100
    severity = _c("HIGH", Fore.RED) if pct >= 50 else (
        _c("MEDIUM", Fore.YELLOW) if pct >= 20 else _c("LOW", Fore.GREEN)
    ) if _COLOUR else (
        "HIGH" if pct >= 50 else "MEDIUM" if pct >= 20 else "LOW"
    )

    header = _c("Extended Diff Score", Fore.CYAN) if _COLOUR else "Extended Diff Score"
    lines.insert(0, f"{header}  ({severity}  {pct:.1f}% weighted impact)")
    lines.insert(1, "-" * 72)
    lines.append("-" * 72)
    lines.append(
        f"  total_weight={score.total_weight:.2f}  "
        f"impact_weight={score.impact_weight:.2f}  "
        f"ratio={score.impact_ratio:.4f}"
    )
    return "\n".join(lines)


def format_extended_score_table(score: ExtendedScore) -> str:
    """Return a compact table of all entries (changed and unchanged)."""
    header = f"{'KEY':<40} {'DOMAIN':<12} {'WEIGHT':>6} {'IMPACT':>7} {'CHG':>4}"
    sep = "-" * len(header)
    rows = [header, sep]
    for e in score.entries:
        chg = "yes" if e.changed else "no"
        rows.append(
            f"{e.key:<40} {e.domain:<12} {e.weight:>6.1f} "
            f"{e.weighted_impact:>7.1f} {chg:>4}"
        )
    rows.append(sep)
    rows.append(
        f"{'TOTAL':<40} {'':<12} {score.total_weight:>6.1f} "
        f"{score.impact_weight:>7.1f} {'':>4}"
    )
    return "\n".join(rows)
