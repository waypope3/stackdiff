"""Render a human-readable baseline comparison report."""
from __future__ import annotations

from stackdiff.baseline import BaselineResult
from stackdiff.reporter import generate_report
from stackdiff.summary_formatter import format_summary

_DIVIDER = "-" * 60


def render_baseline_report(result: BaselineResult, fmt: str = "text") -> str:
    """Return a formatted string for a BaselineResult."""
    header = f"Baseline: {result.snapshot_name}"
    summary_line = str(result.summary)

    if fmt == "json":
        import json
        payload = {
            "baseline": result.snapshot_name,
            "summary": result.summary.as_dict(),
            "diffs": generate_report(result.diffs, fmt="json"),
        }
        return json.dumps(payload, indent=2)

    body = generate_report(result.diffs, fmt=fmt)

    if fmt == "markdown":
        return "\n".join([
            f"## {header}",
            f"> {summary_line}",
            "",
            body,
        ])

    # text (default)
    return "\n".join([
        header,
        _DIVIDER,
        body,
        _DIVIDER,
        summary_line,
    ])
