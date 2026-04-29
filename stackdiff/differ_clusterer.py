"""Cluster diffs by value similarity into named groups."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class ClusteredDiff:
    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    cluster: Optional[str]

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "cluster": self.cluster,
        }

    def __str__(self) -> str:  # pragma: no cover
        marker = "~" if self.changed else "="
        cluster_tag = f"[{self.cluster}]" if self.cluster else "[unclustered]"
        return f"{marker} {self.key}: {self.baseline_value!r} -> {self.target_value!r} {cluster_tag}"


@dataclass
class ClusterResult:
    diffs: List[ClusteredDiff]
    clusters: Dict[str, List[ClusteredDiff]] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "diffs": [d.as_dict() for d in self.diffs],
            "clusters": {
                name: [d.as_dict() for d in members]
                for name, members in self.clusters.items()
            },
        }

    def __str__(self) -> str:  # pragma: no cover
        lines = [f"ClusterResult: {len(self.diffs)} diffs, {len(self.clusters)} clusters"]
        for name, members in self.clusters.items():
            lines.append(f"  {name}: {len(members)} key(s)")
        return "\n".join(lines)


def _assign_cluster(
    key: str,
    value: Optional[str],
    patterns: Dict[str, List[str]],
) -> Optional[str]:
    """Return the first cluster whose patterns match key or value."""
    for cluster_name, pats in patterns.items():
        for pat in pats:
            if fnmatch(key, pat):
                return cluster_name
            if value is not None and fnmatch(value, pat):
                return cluster_name
    return None


def cluster_diffs(
    diffs: Sequence[KeyDiff],
    patterns: Dict[str, List[str]],
) -> ClusterResult:
    """Assign each diff to a named cluster based on key/value glob patterns.

    Args:
        diffs: sequence of KeyDiff objects from the differ.
        patterns: mapping of cluster name -> list of glob patterns tested
                  against key names and target values.

    Returns:
        ClusterResult containing annotated diffs and a cluster index.
    """
    clustered: List[ClusteredDiff] = []
    index: Dict[str, List[ClusteredDiff]] = {name: [] for name in patterns}
    index["unclustered"] = []

    for d in diffs:
        changed = d.baseline_value != d.target_value
        cluster = _assign_cluster(d.key, d.target_value, patterns)
        cd = ClusteredDiff(
            key=d.key,
            baseline_value=d.baseline_value,
            target_value=d.target_value,
            changed=changed,
            cluster=cluster,
        )
        clustered.append(cd)
        bucket = cluster if cluster is not None else "unclustered"
        index.setdefault(bucket, []).append(cd)

    # Remove empty named clusters to keep output tidy
    non_empty = {k: v for k, v in index.items() if v}
    return ClusterResult(diffs=clustered, clusters=non_empty)
