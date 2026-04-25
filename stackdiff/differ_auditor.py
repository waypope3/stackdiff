"""Audit trail for diff operations — records who ran a diff, when, and what changed."""
from __future__ import annotations

import datetime
import getpass
import platform
import socket
from dataclasses import dataclass, field
from typing import List, Optional

from stackdiff.differ import KeyDiff


@dataclass
class AuditEntry:
    key: str
    status: str  # changed | added | removed | unchanged
    baseline_value: Optional[str]
    target_value: Optional[str]

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "status": self.status,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
        }


@dataclass
class AuditRecord:
    run_at: str
    user: str
    hostname: str
    baseline_source: str
    target_source: str
    entries: List[AuditEntry] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "run_at": self.run_at,
            "user": self.user,
            "hostname": self.hostname,
            "baseline_source": self.baseline_source,
            "target_source": self.target_source,
            "entries": [e.as_dict() for e in self.entries],
        }

    def __str__(self) -> str:
        lines = [
            f"Audit  {self.run_at}  user={self.user}  host={self.hostname}",
            f"  baseline : {self.baseline_source}",
            f"  target   : {self.target_source}",
            f"  entries  : {len(self.entries)}",
        ]
        return "\n".join(lines)


def _status(diff: KeyDiff) -> str:
    if diff.baseline_value is None:
        return "added"
    if diff.target_value is None:
        return "removed"
    if diff.baseline_value != diff.target_value:
        return "changed"
    return "unchanged"


def audit_diffs(
    diffs: List[KeyDiff],
    baseline_source: str = "<baseline>",
    target_source: str = "<target>",
) -> AuditRecord:
    """Build an AuditRecord from a list of KeyDiff results."""
    try:
        user = getpass.getuser()
    except Exception:
        user = "unknown"
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = platform.node() or "unknown"

    run_at = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"

    entries = [
        AuditEntry(
            key=d.key,
            status=_status(d),
            baseline_value=d.baseline_value,
            target_value=d.target_value,
        )
        for d in diffs
    ]

    return AuditRecord(
        run_at=run_at,
        user=user,
        hostname=hostname,
        baseline_source=baseline_source,
        target_source=target_source,
        entries=entries,
    )
