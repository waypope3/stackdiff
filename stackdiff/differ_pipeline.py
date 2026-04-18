"""High-level pipeline that wires resolver, parser, filter, sorter and differ."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.resolver import resolve_source
from stackdiff.parser import load_stack
from stackdiff.filter import apply_filters
from stackdiff.sorter import SortOrder, sort_keys
from stackdiff.differ import diff_stacks, KeyDiff
from stackdiff.truncator import truncate_diff


@dataclass
class PipelineOptions:
    include: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)
    sort: SortOrder = SortOrder.ALPHA
    truncate: int = 80
    no_cache: bool = False


@dataclass
class PipelineResult:
    diffs: List[KeyDiff]
    baseline_source: str
    target_source: str


def run_diff_pipeline(
    baseline_uri: str,
    target_uri: str,
    opts: Optional[PipelineOptions] = None,
) -> PipelineResult:
    """Resolve, parse, filter, diff, sort and truncate two stacks."""
    if opts is None:
        opts = PipelineOptions()

    baseline_path = resolve_source(baseline_uri)
    target_path = resolve_source(target_uri)

    baseline_stack = load_stack(baseline_path)
    target_stack = load_stack(target_path)

    baseline_filtered = apply_filters(baseline_stack, opts.include, opts.exclude)
    target_filtered = apply_filters(target_stack, opts.include, opts.exclude)

    raw_diffs = diff_stacks(baseline_filtered, target_filtered)
    sorted_keys = sort_keys(raw_diffs, opts.sort)

    ordered: Dict[str, KeyDiff] = {k: raw_diffs[k] for k in sorted_keys if k in raw_diffs}

    if opts.truncate > 0:
        ordered = truncate_diff(ordered, max_length=opts.truncate)

    return PipelineResult(
        diffs=list(ordered.values()),
        baseline_source=baseline_uri,
        target_source=target_uri,
    )
