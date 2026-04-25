"""End-to-end pipeline that resolves, parses, diffs, and transforms stack outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from stackdiff.differ import diff_stacks
from stackdiff.differ_transformer import TransformedDiff, transform_diffs
from stackdiff.parser import load_stack
from stackdiff.resolver import resolve_source


@dataclass
class TransformedPipelineOptions:
    baseline_uri: str
    target_uri: str
    transforms: List[str] = field(default_factory=list)
    extra_transforms: Optional[Dict[str, Callable[[str], str]]] = None
    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None


@dataclass
class TransformedPipelineResult:
    diffs: List[TransformedDiff]
    transforms_applied: List[str]

    @property
    def has_diff(self) -> bool:
        return any(d.changed for d in self.diffs)

    @property
    def changed_count(self) -> int:
        return sum(1 for d in self.diffs if d.changed)

    @property
    def total_count(self) -> int:
        return len(self.diffs)


def run_transformed_pipeline(opts: TransformedPipelineOptions) -> TransformedPipelineResult:
    """Resolve both sources, diff, then apply transforms and return the result."""
    baseline_path = resolve_source(opts.baseline_uri)
    target_path = resolve_source(opts.target_uri)

    baseline_stack = load_stack(baseline_path)
    target_stack = load_stack(target_path)

    raw_diffs = diff_stacks(baseline_stack, target_stack)

    if opts.include_patterns or opts.exclude_patterns:
        from stackdiff.filter import apply_filters
        raw_diffs = apply_filters(
            raw_diffs,
            include=opts.include_patterns or [],
            exclude=opts.exclude_patterns or [],
        )

    transformed = transform_diffs(
        raw_diffs,
        opts.transforms,
        extra=opts.extra_transforms,
    )

    return TransformedPipelineResult(
        diffs=transformed,
        transforms_applied=list(opts.transforms),
    )
