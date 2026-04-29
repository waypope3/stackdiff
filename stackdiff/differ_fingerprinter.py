"""Fingerprint diffs by hashing key/value pairs for change detection."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Optional

from stackdiff.differ import KeyDiff


@dataclass
class FingerprintedDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    baseline_fingerprint: Optional[str]
    target_fingerprint: Optional[str]
    combined_fingerprint: str

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "baseline_fingerprint": self.baseline_fingerprint,
            "target_fingerprint": self.target_fingerprint,
            "combined_fingerprint": self.combined_fingerprint,
        }

    def __str__(self) -> str:
        marker = "~" if self.changed else "="
        return f"[{marker}] {self.key}  fp={self.combined_fingerprint[:8]}"


def _sha256(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return hashlib.sha256(value.encode()).hexdigest()


def _combined(key: str, baseline: Optional[str], target: Optional[str]) -> str:
    payload = json.dumps({"key": key, "b": baseline, "t": target}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def fingerprint_diffs(diffs: List[KeyDiff]) -> List[FingerprintedDiff]:
    """Return a FingerprintedDiff for every KeyDiff in *diffs*."""
    result: List[FingerprintedDiff] = []
    for d in diffs:
        bfp = _sha256(d.baseline_value)
        tfp = _sha256(d.target_value)
        cfp = _combined(d.key, d.baseline_value, d.target_value)
        changed = d.baseline_value != d.target_value
        result.append(
            FingerprintedDiff(
                key=d.key,
                baseline_value=d.baseline_value,
                target_value=d.target_value,
                changed=changed,
                baseline_fingerprint=bfp,
                target_fingerprint=tfp,
                combined_fingerprint=cfp,
            )
        )
    return result


def stack_fingerprint(diffs: List[FingerprintedDiff]) -> str:
    """Return a single digest summarising the entire diff set."""
    h = hashlib.sha256()
    for d in sorted(diffs, key=lambda x: x.key):
        h.update(d.combined_fingerprint.encode())
    return h.hexdigest()
