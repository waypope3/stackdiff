"""Pipeline variant that produces an indexed diff for downstream lookup."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from stackdiff.differ import KeyDiff, diff_stacks
from stackdiff.differ_indexer import DiffIndex, IndexedDiff, index_diffs
from stackdiff.filter import apply_filters
from stackdiff.parser import load_stack


@dataclass
class IndexedPipelineOptions:
    baseline_path: str
    target_path: str
    include: Optional[List[str]] = None
    exclude: Optional[List[str]] = None


@dataclass
class IndexedPipelineResult:
    diffs: List[KeyDiff]
    index: DiffIndex

    def has_diff(self) -> bool:
        return bool(
            self.index.with_status("changed")
            + self.index.with_status("added")
            + self.index.with_status("removed")
        )

    def lookup(self, key: str) -> Optional[IndexedDiff]:
        return self.index.lookup(key)


def run_indexed_pipeline(opts: IndexedPipelineOptions) -> IndexedPipelineResult:
    """Load two stacks, diff them, apply filters, and build an index."""
    baseline = load_stack(opts.baseline_path)
    target = load_stack(opts.target_path)

    diffs = diff_stacks(baseline, target)

    if opts.include or opts.exclude:
        diffs = apply_filters(
            diffs,
            include=opts.include or [],
            exclude=opts.exclude or [],
        )

    idx = index_diffs(diffs)
    return IndexedPipelineResult(diffs=diffs, index=idx)
