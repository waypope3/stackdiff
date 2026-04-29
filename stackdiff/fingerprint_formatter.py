"""Formatting helpers for FingerprintedDiff results."""
from __future__ import annotations

from typing import List

from stackdiff.differ_fingerprinter import FingerprintedDiff, stack_fingerprint


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _marker(fp: FingerprintedDiff) -> str:
    if fp.baseline_value is None:
        return _c("+", "32")
    if fp.target_value is None:
        return _c("-", "31")
    if fp.changed:
        return _c("~", "33")
    return _c("=", "2")


def format_fingerprinted(
    diffs: List[FingerprintedDiff],
    show_unchanged: bool = False,
    truncate: int = 16,
) -> str:
    lines: List[str] = []
    visible = [d for d in diffs if d.changed or show_unchanged]
    for d in visible:
        m = _marker(d)
        bfp = (d.baseline_fingerprint or "")[:truncate]
        tfp = (d.target_fingerprint or "")[:truncate]
        lines.append(f"  {m} {d.key}")
        lines.append(f"       baseline: {bfp or 'n/a'}")
        lines.append(f"       target:   {tfp or 'n/a'}")
    total = len(diffs)
    changed = sum(1 for d in diffs if d.changed)
    sfp = stack_fingerprint(diffs)[:16]
    lines.append("")
    lines.append(f"  stack fingerprint : {sfp}")
    lines.append(f"  changed / total   : {changed} / {total}")
    return "\n".join(lines)


def format_fingerprinted_table(
    diffs: List[FingerprintedDiff],
    truncate: int = 12,
) -> str:
    header = f"{'KEY':<30}  {'CHANGED':<8}  {'BASELINE FP':<{truncate}}  {'TARGET FP':<{truncate}}"
    sep = "-" * len(header)
    rows = [header, sep]
    for d in diffs:
        bfp = (d.baseline_fingerprint or "n/a")[:truncate]
        tfp = (d.target_fingerprint or "n/a")[:truncate]
        chg = _c("yes", "33") if d.changed else "no"
        rows.append(f"{d.key:<30}  {chg:<8}  {bfp:<{truncate}}  {tfp:<{truncate}}")
    return "\n".join(rows)
