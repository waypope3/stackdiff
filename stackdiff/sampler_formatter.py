"""Format SampledDiff lists for terminal output."""
from __future__ import annotations

from typing import List

from stackdiff.differ_sampler import SampledDiff

try:
    import colorama  # type: ignore
    _RESET = colorama.Style.RESET_ALL
    _GREEN = colorama.Fore.GREEN
    _RED = colorama.Fore.RED
    _YELLOW = colorama.Fore.YELLOW
    _DIM = colorama.Style.DIM
except ImportError:  # pragma: no cover
    _RESET = _GREEN = _RED = _YELLOW = _DIM = ""


def _c(colour: str, text: str) -> str:
    return f"{colour}{text}{_RESET}" if colour else text


def format_sampled(diffs: List[SampledDiff], *, show_excluded: bool = False) -> str:
    """Return a human-readable string for a list of SampledDiff entries.

    Parameters
    ----------
    diffs:
        Output of :func:`~stackdiff.differ_sampler.sample_diffs`.
    show_excluded:
        When True, excluded diffs are shown in dim text so the user can
        see what was omitted.
    """
    lines: List[str] = []
    included = [d for d in diffs if d.included]
    excluded = [d for d in diffs if not d.included]

    lines.append(
        _c(_YELLOW, f"Sample: {len(included)} included, {len(excluded)} excluded")
    )

    for d in included:
        if d.changed:
            line = _c(_RED, f"  ~ {d.key}: {d.baseline_value!r} -> {d.target_value!r}")
        else:
            line = f"    {d.key}: {d.target_value!r}"
        lines.append(line)

    if show_excluded and excluded:
        lines.append(_c(_DIM, f"  ... ({len(excluded)} excluded entries not shown)"))
        for d in excluded:
            lines.append(_c(_DIM, f"  - {d.key}"))

    return "\n".join(lines)


def format_sampled_table(diffs: List[SampledDiff]) -> str:
    """Return a compact table of sampled diffs."""
    included = [d for d in diffs if d.included]
    if not included:
        return "(no sampled diffs)"

    col_w = max(len(d.key) for d in included)
    header = f"  {'KEY':<{col_w}}  STATUS      BASELINE -> TARGET"
    sep = "  " + "-" * (len(header) - 2)
    rows = [header, sep]
    for d in included:
        status = _c(_RED, "changed  ") if d.changed else _c(_GREEN, "unchanged")
        rows.append(f"  {d.key:<{col_w}}  {status}  {d.baseline_value!r} -> {d.target_value!r}")
    return "\n".join(rows)
