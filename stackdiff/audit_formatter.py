"""Format AuditRecord objects for terminal display."""
from __future__ import annotations

import sys
from typing import List

from stackdiff.differ_auditor import AuditRecord, AuditEntry

_COLOURS = {
    "changed": "\033[33m",
    "added": "\033[32m",
    "removed": "\033[31m",
    "unchanged": "\033[90m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


def _c(name: str, text: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{_COLOURS.get(name, '')}{text}{_COLOURS['reset']}"


def _status_marker(status: str) -> str:
    markers = {"changed": "~", "added": "+", "removed": "-", "unchanged": " "}
    return markers.get(status, "?")


def format_audit(record: AuditRecord, show_unchanged: bool = False) -> str:
    lines: List[str] = [
        _c("bold", f"Audit Trail"),
        f"  run_at   : {record.run_at}",
        f"  user     : {record.user}",
        f"  hostname : {record.hostname}",
        f"  baseline : {record.baseline_source}",
        f"  target   : {record.target_source}",
        "",
    ]

    visible = [
        e for e in record.entries
        if show_unchanged or e.status != "unchanged"
    ]

    if not visible:
        lines.append(_c("unchanged", "  (no differences)"))
    else:
        for entry in visible:
            marker = _status_marker(entry.status)
            key_part = _c(entry.status, f"{marker} {entry.key}")
            if entry.status == "changed":
                lines.append(f"  {key_part}")
                lines.append(f"      before: {entry.baseline_value}")
                lines.append(f"      after : {entry.target_value}")
            elif entry.status == "added":
                lines.append(f"  {key_part}  => {entry.target_value}")
            elif entry.status == "removed":
                lines.append(f"  {key_part}  (was: {entry.baseline_value})")
            else:
                lines.append(f"  {key_part}  {entry.baseline_value}")

    summary_parts = [
        f"changed={sum(1 for e in record.entries if e.status == 'changed')}",
        f"added={sum(1 for e in record.entries if e.status == 'added')}",
        f"removed={sum(1 for e in record.entries if e.status == 'removed')}",
        f"unchanged={sum(1 for e in record.entries if e.status == 'unchanged')}",
    ]
    lines.append("")
    lines.append("  " + "  ".join(summary_parts))
    return "\n".join(lines)
