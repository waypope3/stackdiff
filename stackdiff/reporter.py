"""Generate structured reports from diff results."""
from __future__ import annotations

import json
from typing import Literal

from stackdiff.differ import DiffResult

ReportFormat = Literal["text", "json", "markdown"]


def _text_report(result: DiffResult) -> str:
    lines: list[str] = []
    for key, (old, new) in sorted(result.changed.items()):
        lines.append(f"~ {key}: {old!r} -> {new!r}")
    for key, value in sorted(result.added.items()):
        lines.append(f"+ {key}: {value!r}")
    for key, value in sorted(result.removed.items()):
        lines.append(f"- {key}: {value!r}")
    if not lines:
        return "No differences found."
    return "\n".join(lines)


def _json_report(result: DiffResult) -> str:
    payload = {
        "changed": {
            k: {"old": old, "new": new}
            for k, (old, new) in result.changed.items()
        },
        "added": dict(result.added),
        "removed": dict(result.removed),
        "unchanged": dict(result.unchanged),
    }
    return json.dumps(payload, indent=2)


def _markdown_report(result: DiffResult) -> str:
    lines = ["# Stack Diff Report", ""]
    if result.changed:
        lines.append("## Changed")
        for key, (old, new) in sorted(result.changed.items()):
            lines.append(f"- **{key}**: `{old}` → `{new}`")
        lines.append("")
    if result.added:
        lines.append("## Added")
        for key, value in sorted(result.added.items()):
            lines.append(f"- **{key}**: `{value}`")
        lines.append("")
    if result.removed:
        lines.append("## Removed")
        for key, value in sorted(result.removed.items()):
            lines.append(f"- **{key}**: `{value}`")
        lines.append("")
    if not (result.changed or result.added or result.removed):
        lines.append("_No differences found._")
    return "\n".join(lines)


def generate_report(result: DiffResult, fmt: ReportFormat = "text") -> str:
    """Return a formatted report string for *result*."""
    if fmt == "json":
        return _json_report(result)
    if fmt == "markdown":
        return _markdown_report(result)
    return _text_report(result)
