"""Export diff results to various file formats."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Literal

from stackdiff.differ import DiffResult

ExportFormat = Literal["json", "csv", "markdown"]


class ExportError(Exception):
    """Raised when export fails."""


def _to_json(result: DiffResult) -> str:
    rows = [
        {"key": k, "baseline": v.get("baseline"), "target": v.get("target"), "status": v.get("status")}
        for k, v in result.items()
    ]
    return json.dumps(rows, indent=2)


def _to_csv(result: DiffResult) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["key", "baseline", "target", "status"])
    writer.writeheader()
    for key, val in result.items():
        writer.writerow({
            "key": key,
            "baseline": val.get("baseline", ""),
            "target": val.get("target", ""),
            "status": val.get("status", ""),
        })
    return buf.getvalue()


def _to_markdown(result: DiffResult) -> str:
    lines = ["| Key | Baseline | Target | Status |", "|-----|----------|--------|--------|"]
    for key, val in result.items():
        lines.append(
            f"| {key} | {val.get('baseline', '')} | {val.get('target', '')} | {val.get('status', '')} |"
        )
    return "\n".join(lines) + "\n"


def export_diff(result: DiffResult, fmt: ExportFormat, dest: Path) -> None:
    """Serialise *result* in *fmt* and write to *dest*."""
    if fmt == "json":
        text = _to_json(result)
    elif fmt == "csv":
        text = _to_csv(result)
    elif fmt == "markdown":
        text = _to_markdown(result)
    else:
        raise ExportError(f"Unknown export format: {fmt!r}")

    try:
        dest.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise ExportError(f"Could not write to {dest}: {exc}") from exc
