"""differ_scorer2: extended scoring with weighted change penalties per key domain."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from stackdiff.differ import KeyDiff


_DOMAIN_WEIGHTS: dict[str, float] = {
    "iam": 3.0,
    "network": 2.5,
    "database": 2.0,
    "storage": 1.5,
    "compute": 1.2,
    "default": 1.0,
}

_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "iam": ["role", "policy", "permission", "arn", "principal"],
    "network": ["vpc", "subnet", "cidr", "sg", "securitygroup", "route"],
    "database": ["db", "rds", "endpoint", "cluster", "aurora"],
    "storage": ["bucket", "s3", "efs", "volume"],
    "compute": ["instance", "asg", "lambda", "function", "ecs"],
}


def _infer_domain(key: str) -> str:
    lower = key.lower()
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return domain
    return "default"


@dataclass
class WeightedScore:
    key: str
    domain: str
    weight: float
    changed: bool
    weighted_impact: float

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "domain": self.domain,
            "weight": self.weight,
            "changed": self.changed,
            "weighted_impact": self.weighted_impact,
        }


@dataclass
class ExtendedScore:
    entries: List[WeightedScore] = field(default_factory=list)
    total_weight: float = 0.0
    impact_weight: float = 0.0

    @property
    def impact_ratio(self) -> float:
        if self.total_weight == 0:
            return 0.0
        return round(self.impact_weight / self.total_weight, 4)

    def as_dict(self) -> dict:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "total_weight": self.total_weight,
            "impact_weight": self.impact_weight,
            "impact_ratio": self.impact_ratio,
        }

    def __str__(self) -> str:
        pct = self.impact_ratio * 100
        return (
            f"ExtendedScore(impact={pct:.1f}%, "
            f"impact_weight={self.impact_weight:.2f}, "
            f"total_weight={self.total_weight:.2f})"
        )


def score_diffs_extended(
    diffs: List[KeyDiff],
    domain_weights: Optional[dict[str, float]] = None,
) -> ExtendedScore:
    """Score diffs using per-domain weights to reflect operational risk."""
    weights = {**_DOMAIN_WEIGHTS, **(domain_weights or {})}
    entries: List[WeightedScore] = []
    total_w = 0.0
    impact_w = 0.0

    for d in diffs:
        domain = _infer_domain(d.key)
        w = weights.get(domain, weights["default"])
        changed = d.baseline != d.target
        impact = w if changed else 0.0
        entries.append(WeightedScore(
            key=d.key,
            domain=domain,
            weight=w,
            changed=changed,
            weighted_impact=impact,
        ))
        total_w += w
        impact_w += impact

    return ExtendedScore(entries=entries, total_weight=total_w, impact_weight=impact_w)
