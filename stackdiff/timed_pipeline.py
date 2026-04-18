"""Thin wrapper that runs the core stackdiff pipeline with profiling."""
from __future__ import annotations

from typing import Optional

from stackdiff.differ import DiffResult, diff_stacks
from stackdiff.filter import apply_filters
from stackdiff.parser import load_stack
from stackdiff.profiler import Profile, Profiler
from stackdiff.resolver import resolve_source
from stackdiff.sorter import SortOrder, sort_keys
from stackdiff.truncator import truncate_diff


def run_pipeline(
    baseline_uri: str,
    target_uri: str,
    include: Optional[list] = None,
    exclude: Optional[list] = None,
    sort_order: SortOrder = SortOrder.ALPHA,
    truncate: bool = False,
    max_value_len: int = 80,
) -> tuple[DiffResult, Profile]:
    """Execute the full diff pipeline, returning the result and timing profile."""
    profiler = Profiler()

    with profiler.stage("resolve_baseline"):
        raw_baseline = resolve_source(baseline_uri)

    with profiler.stage("resolve_target"):
        raw_target = resolve_source(target_uri)

    with profiler.stage("parse_baseline"):
        baseline = load_stack(raw_baseline)

    with profiler.stage("parse_target"):
        target = load_stack(raw_target)

    with profiler.stage("filter"):
        baseline = apply_filters(baseline, include=include, exclude=exclude)
        target = apply_filters(target, include=include, exclude=exclude)

    with profiler.stage("diff"):
        result = diff_stacks(baseline, target)

    with profiler.stage("sort"):
        result = DiffResult(
            changed=dict(sort_keys(result.changed, sort_order)),
            added=dict(sort_keys(result.added, sort_order)),
            removed=dict(sort_keys(result.removed, sort_order)),
            unchanged=dict(sort_keys(result.unchanged, sort_order)),
        )

    if truncate:
        with profiler.stage("truncate"):
            result = truncate_diff(result, max_len=max_value_len)

    return result, profiler.profile
