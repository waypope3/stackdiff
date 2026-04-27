"""Annotate diffs with contextual metadata derived from key patterns and value types."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from stackdiff.differ import KeyDiff


_ARN_RE = re.compile(r"^arn:[a-z0-9\-]+:")
_URL_RE = re.compile(r"^https?://")
_CIDR_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}/\d{1,2}$")

_DOMAIN_PATTERNS: List[tuple[str, str]] = [
    (r"(?i)(vpc|subnet|sg|security.?group)", "network"),
    (r"(?i)(db|database|rds|aurora)", "database"),
    (r"(?i)(bucket|s3|object)", "storage"),
    (r"(?i)(role|policy|iam|permission)", "iam"),
    (r"(?i)(lambda|function|handler)", "compute"),
    (r"(?i)(queue|topic|sns|sqs)", "messaging"),
]


def _infer_value_hint(value: Optional[str]) -> Optional[str]:
    if not isinstance(value, str) or not value:
        return None
    if _ARN_RE.match(value):
        return "arn"
    if _URL_RE.match(value):
        return "url"
    if _CIDR_RE.match(value):
        return "cidr"
    return None


def _infer_domain(key: str) -> Optional[str]:
    for pattern, domain in _DOMAIN_PATTERNS:
        if re.search(pattern, key):
            return domain
    return None


@dataclass
class AnnotatedDiff2:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    domain: Optional[str]
    value_hint: Optional[str]
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "domain": self.domain,
            "value_hint": self.value_hint,
            "notes": self.notes,
        }

    def __str__(self) -> str:
        marker = "~" if self.changed else "="
        domain_tag = f"[{self.domain}]" if self.domain else ""
        hint_tag = f"({self.value_hint})" if self.value_hint else ""
        return f"{marker} {self.key}{domain_tag}{hint_tag}: {self.baseline_value!r} -> {self.target_value!r}"


def annotate_diffs2(diffs: List[KeyDiff]) -> List[AnnotatedDiff2]:
    """Return AnnotatedDiff2 instances enriched with domain and value hints."""
    results: List[AnnotatedDiff2] = []
    for d in diffs:
        changed = d.baseline_value != d.target_value
        domain = _infer_domain(d.key)
        hint = _infer_value_hint(d.target_value) or _infer_value_hint(d.baseline_value)
        notes: List[str] = []
        if d.baseline_value is None:
            notes.append("added")
        elif d.target_value is None:
            notes.append("removed")
        elif changed:
            notes.append("modified")
        results.append(
            AnnotatedDiff2(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=changed,
                domain=domain,
                value_hint=hint,
                notes=notes,
            )
        )
    return results
