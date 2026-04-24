"""Aggregate multiple diff results into a single consolidated view."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.differ import KeyDiff


@dataclass
class AggregatedDiff:
    key: str
    values: Dict[str, Optional[str]]  # source_label -> value
    baseline_value: Optional[str]
    is_consistent: bool  # True if all sources agree
    sources: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "is_consistent": self.is_consistent,
            "sources": self.sources,
            "values": self.values,
        }

    def __str__(self) -> str:
        status = "OK" if self.is_consistent else "DIVERGED"
        return f"{self.key} [{status}]: {self.values}"


def _all_equal(values: List[Optional[str]]) -> bool:
    return len(set(v for v in values)) <= 1


def aggregate_diffs(
    baseline: List[KeyDiff],
    sources: Dict[str, List[KeyDiff]],
) -> List[AggregatedDiff]:
    """Aggregate diffs from multiple named sources against a common baseline.

    Args:
        baseline: The reference diff list (e.g. from a baseline stack).
        sources: Mapping of source label to its diff list.

    Returns:
        List of AggregatedDiff, one per unique key across all inputs.
    """
    all_keys: List[str] = []
    seen: set = set()
    for d in baseline:
        if d.key not in seen:
            all_keys.append(d.key)
            seen.add(d.key)
    for diffs in sources.values():
        for d in diffs:
            if d.key not in seen:
                all_keys.append(d.key)
                seen.add(d.key)

    baseline_map: Dict[str, Optional[str]] = {d.key: d.baseline for d in baseline}
    source_maps: Dict[str, Dict[str, Optional[str]]] = {
        label: {d.key: d.target for d in diffs}
        for label, diffs in sources.items()
    }
    source_labels = list(sources.keys())

    results: List[AggregatedDiff] = []
    for key in all_keys:
        base_val = baseline_map.get(key)
        vals: Dict[str, Optional[str]] = {
            label: source_maps[label].get(key) for label in source_labels
        }
        consistent = _all_equal(list(vals.values()))
        results.append(
            AggregatedDiff(
                key=key,
                values=vals,
                baseline_value=base_val,
                is_consistent=consistent,
                sources=source_labels,
            )
        )
    return results
