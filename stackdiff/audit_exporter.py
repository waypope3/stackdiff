"""Export AuditRecord to JSON or CSV for compliance / archival purposes."""
from __future__ import annotations

import csv
import io
import json
from typing import Literal

from stackdiff.differ_auditor import AuditRecord

ExportFormat = Literal["json", "csv"]


class AuditExportError(Exception):
    """Raised when an unsupported export format is requested."""


def _to_json(record: AuditRecord) -> str:
    return json.dumps(record.as_dict(), indent=2)


def _to_csv(record: AuditRecord) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["run_at", "user", "hostname", "baseline_source",
                     "target_source", "key", "status",
                     "baseline_value", "target_value"])
    for entry in record.entries:
        writer.writerow([
            record.run_at,
            record.user,
            record.hostname,
            record.baseline_source,
            record.target_source,
            entry.key,
            entry.status,
            entry.baseline_value if entry.baseline_value is not None else "",
            entry.target_value if entry.target_value is not None else "",
        ])
    return buf.getvalue()


def export_audit(record: AuditRecord, fmt: ExportFormat = "json") -> str:
    """Serialise *record* to the requested format string.

    Supported formats: ``json``, ``csv``.
    Raises :class:`AuditExportError` for unknown formats.
    """
    if fmt == "json":
        return _to_json(record)
    if fmt == "csv":
        return _to_csv(record)
    raise AuditExportError(f"Unsupported audit export format: {fmt!r}")
