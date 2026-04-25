"""Format ValidatedDiff results for terminal output."""
from __future__ import annotations

from typing import Sequence

from stackdiff.differ_validator import ValidatedDiff

try:
    import colorama  # type: ignore
    colorama.init(autoreset=True)
    _RED = colorama.Fore.RED
    _GREEN = colorama.Fore.GREEN
    _YELLOW = colorama.Fore.YELLOW
    _RESET = colorama.Style.RESET_ALL
except ImportError:  # pragma: no cover
    _RED = _GREEN = _YELLOW = _RESET = ""


def _c(text: str, colour: str) -> str:
    return f"{colour}{text}{_RESET}" if colour else text


def format_validated(diffs: Sequence[ValidatedDiff], *, show_ok: bool = True) -> str:
    """Return a human-readable validation report."""
    lines: list[str] = []
    violation_count = 0

    for d in diffs:
        if d.has_violation:
            violation_count += 1
            marker = _c("✗", _RED)
            key_str = _c(d.key, _RED)
            lines.append(f"  {marker} {key_str}")
            for v in d.violations:
                lines.append(f"      {_c(v, _YELLOW)}")
        elif show_ok:
            marker = _c("✓", _GREEN)
            lines.append(f"  {marker} {d.key}")

    total = len(diffs)
    summary = _c(
        f"Violations: {violation_count}/{total}",
        _RED if violation_count else _GREEN,
    )
    lines.append("")
    lines.append(summary)
    return "\n".join(lines)


def format_validated_table(diffs: Sequence[ValidatedDiff]) -> str:
    """Return a compact table of only violating diffs."""
    violating = [d for d in diffs if d.has_violation]
    if not violating:
        return _c("No validation violations found.", _GREEN)

    col_w = max(len(d.key) for d in violating) + 2
    header = f"{'KEY':<{col_w}}  VIOLATIONS"
    sep = "-" * (col_w + 30)
    rows = [header, sep]
    for d in violating:
        msgs = "; ".join(d.violations)
        rows.append(f"{d.key:<{col_w}}  {_c(msgs, _RED)}")
    return "\n".join(rows)
