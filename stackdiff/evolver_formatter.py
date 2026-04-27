"""evolver_formatter: render EvolvedDiff results as coloured text tables."""
from __future__ import annotations

from typing import List, Sequence

from stackdiff.differ_evolver import EvolvedDiff

try:
    import colorama  # type: ignore
    _RESET = colorama.Style.RESET_ALL
    _BOLD = colorama.Style.BRIGHT
    _RED = colorama.Fore.RED
    _GREEN = colorama.Fore.GREEN
    _YELLOW = colorama.Fore.YELLOW
    _CYAN = colorama.Fore.CYAN
except ImportError:  # pragma: no cover
    _RESET = _BOLD = _RED = _GREEN = _YELLOW = _CYAN = ""


_TREND_COLOUR = {
    "stable": _GREEN,
    "growing": _CYAN,
    "shrinking": _YELLOW,
    "volatile": _RED,
}


def _c(colour: str, text: str) -> str:
    return f"{colour}{text}{_RESET}" if colour else text


def _marker(evolved: EvolvedDiff) -> str:
    if evolved.changed:
        return _c(_RED, "~")
    return _c(_GREEN, "=")


def format_evolved(evolveds: Sequence[EvolvedDiff], *, show_stable: bool = False) -> str:
    """Return a compact per-key evolution summary."""
    lines: List[str] = []
    for ev in evolveds:
        if not show_stable and not ev.changed:
            continue
        trend_str = _c(_TREND_COLOUR.get(ev.trend, ""), ev.trend)
        lines.append(
            f"{_marker(ev)} {_c(_BOLD, ev.key):<40}  "
            f"changes={ev.change_count}  trend={trend_str}  "
            f"last={ev.last_seen!r}"
        )
    if not lines:
        return "(no evolution changes detected)\n"
    return "\n".join(lines) + "\n"


def format_evolved_table(evolveds: Sequence[EvolvedDiff], *, show_stable: bool = False) -> str:
    """Return a tabular evolution report with a header row."""
    header = (
        f"{'KEY':<40}  {'CHANGES':>7}  {'TREND':<10}  {'FIRST VALUE':<30}  LAST VALUE"
    )
    sep = "-" * len(header)
    rows: List[str] = [header, sep]
    for ev in evolveds:
        if not show_stable and not ev.changed:
            continue
        trend_str = _c(_TREND_COLOUR.get(ev.trend, ""), f"{ev.trend:<10}")
        rows.append(
            f"{ev.key:<40}  {ev.change_count:>7}  {trend_str}  "
            f"{str(ev.first_seen):<30}  {ev.last_seen!r}"
        )
    if len(rows) == 2:  # only header
        rows.append("  (no evolution changes detected)")
    return "\n".join(rows) + "\n"
