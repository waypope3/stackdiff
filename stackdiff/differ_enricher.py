"""Enrich diffs with metadata derived from key patterns and value types."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from stackdiff.differ import KeyDiff


_ARN_RE = re.compile(r"^arn:[a-z0-9\-]+:[a-z0-9\-]+:")
_URL_RE = re.compile(r"^https?://")
_CIDR_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}/\d{1,2}$")
_ACCOUNT_RE = re.compile(r"^\d{12}$")


def _infer_value_type(value: Optional[str]) -> str:
    """Return a short label describing the shape of *value*."""
    if value is None:
        return "null"
    if _ARN_RE.match(value):
        return "arn"
    if _URL_RE.match(value):
        return "url"
    if _CIDR_RE.match(value):
        return "cidr"
    if _ACCOUNT_RE.match(value):
        return "account_id"
    return "string"


def _infer_key_domain(key: str) -> str:
    """Return a broad domain label based on the key name."""
    lower = key.lower()
    if any(t in lower for t in ("vpc", "subnet", "cidr", "sg", "securitygroup")):
        return "network"
    if any(t in lower for t in ("bucket", "table", "volume", "snapshot")):
        return "storage"
    if any(t in lower for t in ("role", "policy", "user", "permission")):
        return "iam"
    if any(t in lower for t in ("db", "rds", "cluster", "endpoint")):
        return "database"
    if any(t in lower for t in ("lambda", "function", "queue", "topic", "stream")):
        return "compute"
    return "general"


@dataclass
class EnrichedDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    baseline_type: str
    target_type: str
    domain: str
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "baseline_type": self.baseline_type,
            "target_type": self.target_type,
            "domain": self.domain,
            "notes": self.notes,
        }


def enrich_diffs(diffs: List[KeyDiff]) -> List[EnrichedDiff]:
    """Return an :class:`EnrichedDiff` for every entry in *diffs*."""
    enriched: List[EnrichedDiff] = []
    for d in diffs:
        bt = _infer_value_type(d.baseline_value)
        tt = _infer_value_type(d.target_value)
        notes: List[str] = []
        if bt != tt:
            notes.append(f"type changed: {bt} -> {tt}")
        enriched.append(
            EnrichedDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=d.baseline_value != d.target_value,
                baseline_type=bt,
                target_type=tt,
                domain=_infer_key_domain(d.key),
                notes=notes,
            )
        )
    return enriched
