"""differ_reconciler.py – reconcile diffs against an expected/desired state.

Given a list of KeyDiff results and a mapping of expected values, produces
ReconciledDiff instances that indicate whether each key is *compliant*
(actual matches expected), *non-compliant* (actual differs from expected),
*untracked* (no expectation defined), or *missing* (expected but absent).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional, Sequence

from stackdiff.differ import KeyDiff

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STATUS_COMPLIANT = "compliant"
STATUS_NON_COMPLIANT = "non_compliant"
STATUS_UNTRACKED = "untracked"
STATUS_MISSING = "missing"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class ReconciledDiff:
    """A KeyDiff decorated with reconciliation metadata."""

    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    expected_value: Optional[str]
    changed: bool
    status: str  # one of the STATUS_* constants above
    note: str = ""

    def as_dict(self) -> Dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "expected_value": self.expected_value,
            "changed": self.changed,
            "status": self.status,
            "note": self.note,
        }

    def __str__(self) -> str:  # pragma: no cover
        marker = "✓" if self.status == STATUS_COMPLIANT else "✗"
        return (
            f"{marker} [{self.status}] {self.key}: "
            f"target={self.target_value!r} expected={self.expected_value!r}"
        )


@dataclass
class ReconcileResult:
    """Aggregated output of a reconciliation run."""

    diffs: List[ReconciledDiff] = field(default_factory=list)

    # synthetic entries for keys that are expected but entirely absent
    missing: List[ReconciledDiff] = field(default_factory=list)

    def as_dict(self) -> Dict:
        return {
            "diffs": [d.as_dict() for d in self.diffs],
            "missing": [d.as_dict() for d in self.missing],
            "compliant_count": self.compliant_count,
            "non_compliant_count": self.non_compliant_count,
            "untracked_count": self.untracked_count,
            "missing_count": self.missing_count,
        }

    @property
    def compliant_count(self) -> int:
        return sum(1 for d in self.diffs if d.status == STATUS_COMPLIANT)

    @property
    def non_compliant_count(self) -> int:
        return sum(1 for d in self.diffs if d.status == STATUS_NON_COMPLIANT)

    @property
    def untracked_count(self) -> int:
        return sum(1 for d in self.diffs if d.status == STATUS_UNTRACKED)

    @property
    def missing_count(self) -> int:
        return len(self.missing)

    @property
    def has_violations(self) -> bool:
        return self.non_compliant_count > 0 or self.missing_count > 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _match_expected(key: str, expectations: Dict[str, str]) -> Optional[str]:
    """Return the expected value for *key*, supporting glob patterns.

    Exact matches take priority; glob patterns are evaluated in insertion order.
    Returns ``None`` when no expectation is defined.
    """
    if key in expectations:
        return expectations[key]
    for pattern, value in expectations.items():
        if fnmatch(key, pattern):
            return value
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def reconcile_diffs(
    diffs: Sequence[KeyDiff],
    expectations: Dict[str, str],
) -> ReconcileResult:
    """Reconcile *diffs* against *expectations*.

    Parameters
    ----------
    diffs:
        The sequence of :class:`~stackdiff.differ.KeyDiff` objects produced by
        :func:`~stackdiff.differ.diff_stacks`.
    expectations:
        A mapping of key (or glob pattern) → expected target value.  Keys
        present in *expectations* but absent from *diffs* are reported as
        *missing* entries in the result.

    Returns
    -------
    ReconcileResult
    """
    seen_keys: set[str] = set()
    reconciled: List[ReconciledDiff] = []

    for diff in diffs:
        expected = _match_expected(diff.key, expectations)
        seen_keys.add(diff.key)

        if expected is None:
            status = STATUS_UNTRACKED
            note = "No expectation defined for this key."
        elif diff.target_value == expected:
            status = STATUS_COMPLIANT
            note = ""
        else:
            status = STATUS_NON_COMPLIANT
            note = f"Expected {expected!r}, got {diff.target_value!r}."

        reconciled.append(
            ReconciledDiff(
                key=diff.key,
                baseline_value=diff.baseline_value,
                target_value=diff.target_value,
                expected_value=expected,
                changed=diff.baseline_value != diff.target_value,
                status=status,
                note=note,
            )
        )

    # Identify expected keys that were not present in diffs at all.
    missing: List[ReconciledDiff] = []
    for pattern, expected_value in expectations.items():
        # Skip glob patterns — we can't synthesise a concrete key for them.
        if any(c in pattern for c in ("*", "?", "[")):
            continue
        if pattern not in seen_keys:
            missing.append(
                ReconciledDiff(
                    key=pattern,
                    baseline_value=None,
                    target_value=None,
                    expected_value=expected_value,
                    changed=False,
                    status=STATUS_MISSING,
                    note=f"Key {pattern!r} expected but not found in either stack.",
                )
            )

    return ReconcileResult(diffs=reconciled, missing=missing)
