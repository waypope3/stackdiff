"""End-to-end pipeline that loads stacks, diffs them, and correlates changes."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence

from stackdiff.parser import load_stack
from stackdiff.differ import diff_stacks
from stackdiff.differ_correlator import CorrelatedDiff, correlate_diffs


@dataclass
class CorrelatedPipelineOptions:
    baseline_path: str
    target_path: str
    history_paths: List[str] = field(default_factory=list)


@dataclass
class CorrelatedPipelineResult:
    diffs: List[CorrelatedDiff]
    changed_count: int
    total_count: int

    @property
    def has_diff(self) -> bool:
        return self.changed_count > 0


def run_correlated_pipeline(
    opts: CorrelatedPipelineOptions,
) -> CorrelatedPipelineResult:
    baseline = load_stack(Path(opts.baseline_path))
    target = load_stack(Path(opts.target_path))
    primary = diff_stacks(baseline, target)

    history = []
    for i in range(0, len(opts.history_paths) - 1, 2):
        try:
            h_base = load_stack(Path(opts.history_paths[i]))
            h_tgt = load_stack(Path(opts.history_paths[i + 1]))
            history.append(diff_stacks(h_base, h_tgt))
        except Exception:
            pass

    correlated = correlate_diffs(primary, history)
    changed = sum(1 for d in correlated if d.changed)
    return CorrelatedPipelineResult(
        diffs=correlated,
        changed_count=changed,
        total_count=len(correlated),
    )
