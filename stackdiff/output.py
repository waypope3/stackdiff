"""Write reports to a file or stdout."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from stackdiff.differ import DiffResult
from stackdiff.reporter import ReportFormat, generate_report


def write_report(
    result: DiffResult,
    fmt: ReportFormat = "text",
    output_path: Optional[str] = None,
) -> None:
    """Generate a report and write it to *output_path* or stdout."""
    content = generate_report(result, fmt=fmt)
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
    else:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
