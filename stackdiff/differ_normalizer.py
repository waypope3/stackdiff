"""Normalize diff keys and values for consistent comparison.

Provides utilities to strip whitespace, normalise casing on keys,
and coerce common value representations before diffing.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from stackdiff.differ import KeyDiff


@dataclass
class NormalizedDiff:
    key: str
    baseline_raw: Any
    target_raw: Any
    baseline_norm: str
    target_norm: str
    changed: bool

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_raw": self.baseline_raw,
            "target_raw": self.target_raw,
            "baseline_norm": self.baseline_norm,
            "target_norm": self.target_norm,
            "changed": self.changed,
        }


_TRUTHY = {"true", "yes", "1", "on"}
_FALSY = {"false", "no", "0", "off"}


def _normalise_value(value: Any) -> str:
    """Return a canonical string representation of *value*."""
    if value is None:
        return ""
    s = str(value).strip()
    lower = s.lower()
    if lower in _TRUTHY:
        return "true"
    if lower in _FALSY:
        return "false"
    return s


def _normalise_key(key: str) -> str:
    """Strip and lower-case a key for case-insensitive comparison."""
    return key.strip().lower()


def normalize_diffs(
    diffs: list[KeyDiff],
    *,
    case_insensitive_keys: bool = False,
) -> list[NormalizedDiff]:
    """Return *NormalizedDiff* entries derived from *diffs*.

    Parameters
    ----------
    diffs:
        Raw :class:`~stackdiff.differ.KeyDiff` entries.
    case_insensitive_keys:
        When *True* the ``key`` stored on each result is lower-cased so that
        keys differing only in case are treated as the same key.
    """
    results: list[NormalizedDiff] = []
    for d in diffs:
        key = _normalise_key(d.key) if case_insensitive_keys else d.key
        b_norm = _normalise_value(d.baseline)
        t_norm = _normalise_value(d.target)
        results.append(
            NormalizedDiff(
                key=key,
                baseline_raw=d.baseline,
                target_raw=d.target,
                baseline_norm=b_norm,
                target_norm=t_norm,
                changed=b_norm != t_norm,
            )
        )
    return results
