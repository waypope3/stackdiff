"""Correlate diffs across multiple stack comparisons to find co-changing keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class CorrelatedDiff:
    key: str
    baseline_value: str
    target_value: str
    changed: bool
    co_changed_with: List[str] = field(default_factory=list)
    correlation_score: float = 0.0

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "co_changed_with": self.co_changed_with,
            "correlation_score": round(self.correlation_score, 4),
        }

    def __str__(self) -> str:
        marker = "~" if self.changed else "="
        co = ", ".join(self.co_changed_with) if self.co_changed_with else "none"
        return (
            f"[{marker}] {self.key}: {self.baseline_value!r} -> {self.target_value!r} "
            f"(co-changes: {co}, score: {self.correlation_score:.4f})"
        )


def _changed_keys(diffs: Sequence[KeyDiff]) -> frozenset:
    return frozenset(d.key for d in diffs if d.baseline != d.target)


def correlate_diffs(
    primary: Sequence[KeyDiff],
    history: Sequence[Sequence[KeyDiff]],
) -> List[CorrelatedDiff]:
    """For each changed key in *primary*, find keys that changed together
    across *history* snapshots and compute a Jaccard-based correlation score."""
    primary_changed = _changed_keys(primary)
    history_changed_sets = [_changed_keys(h) for h in history]

    # Build co-occurrence counts for all key pairs across history
    co_counts: Dict[str, Dict[str, int]] = {}
    change_counts: Dict[str, int] = {}
    for changed_set in history_changed_sets:
        for k in changed_set:
            change_counts[k] = change_counts.get(k, 0) + 1
            for other in changed_set:
                if other == k:
                    continue
                co_counts.setdefault(k, {})
                co_counts[k][other] = co_counts[k].get(other, 0) + 1

    results: List[CorrelatedDiff] = []
    for diff in primary:
        changed = diff.baseline != diff.target
        co_changed: List[str] = []
        score = 0.0

        if changed and diff.key in co_counts:
            peers = co_counts[diff.key]
            # Jaccard: |A∩B| / |A∪B| over history windows
            a_count = change_counts.get(diff.key, 0)
            scored = []
            for peer_key, ab in peers.items():
                b_count = change_counts.get(peer_key, 0)
                union = a_count + b_count - ab
                jaccard = ab / union if union > 0 else 0.0
                if jaccard > 0:
                    scored.append((peer_key, jaccard))
            scored.sort(key=lambda x: -x[1])
            if scored:
                co_changed = [k for k, _ in scored]
                score = scored[0][1]

        results.append(
            CorrelatedDiff(
                key=diff.key,
                baseline_value=diff.baseline,
                target_value=diff.target,
                changed=changed,
                co_changed_with=co_changed,
                correlation_score=score,
            )
        )
    return results
