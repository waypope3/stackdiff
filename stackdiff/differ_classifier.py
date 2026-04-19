"""Classify diffs into named change categories."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from stackdiff.differ import KeyDiff

_CATEGORY_PATTERNS: Dict[str, List[str]] = {
    "network": ["vpc", "subnet", "cidr", "sg", "security", "route", "gateway"],
    "compute": ["instance", "ami", "ec2", "asg", "launch", "cpu", "memory"],
    "storage": ["bucket", "s3", "efs", "ebs", "volume", "disk"],
    "database": ["rds", "db", "database", "postgres", "mysql", "aurora"],
    "iam": ["role", "policy", "arn", "permission", "iam", "user"],
}


def _classify(key: str) -> str:
    lower = key.lower()
    for category, patterns in _CATEGORY_PATTERNS.items():
        if any(p in lower for p in patterns):
            return category
    return "general"


@dataclass
class ClassifiedDiff:
    key: str
    baseline: object
    current: object
    changed: bool
    category: str

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline": self.baseline,
            "current": self.current,
            "changed": self.changed,
            "category": self.category,
        }


def classify_diffs(diffs: List[KeyDiff]) -> List[ClassifiedDiff]:
    """Return a ClassifiedDiff for every KeyDiff."""
    return [
        ClassifiedDiff(
            key=d.key,
            baseline=d.baseline,
            current=d.current,
            changed=d.changed,
            category=_classify(d.key),
        )
        for d in diffs
    ]


def group_by_category(classified: List[ClassifiedDiff]) -> Dict[str, List[ClassifiedDiff]]:
    """Group ClassifiedDiff list by category name."""
    result: Dict[str, List[ClassifiedDiff]] = {}
    for item in classified:
        result.setdefault(item.category, []).append(item)
    return result
