"""Convenience pipeline: resolve, parse, diff, and map keys in one call."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.differ import diff_stacks
from stackdiff.differ_mapper import MappedDiff, map_diffs
from stackdiff.parser import load_stack
from stackdiff.resolver import resolve_source


@dataclass
class MappedPipelineOptions:
    """Configuration for :func:`run_mapped_pipeline`."""

    baseline_uri: str
    target_uri: str
    #: Key-translation table applied after diffing.
    mapping: Dict[str, str] = field(default_factory=dict)
    #: When *True* only changed keys are returned.
    changed_only: bool = False


@dataclass
class MappedPipelineResult:
    """Output of :func:`run_mapped_pipeline`."""

    diffs: List[MappedDiff]
    baseline_uri: str
    target_uri: str
    mapping_applied: Dict[str, str]

    @property
    def has_diff(self) -> bool:
        return any(d.changed for d in self.diffs)


def run_mapped_pipeline(opts: MappedPipelineOptions) -> MappedPipelineResult:
    """Resolve sources, diff them, and apply the key mapping.

    Parameters
    ----------
    opts:
        Pipeline configuration including URIs and optional key mapping.

    Returns
    -------
    MappedPipelineResult
        Fully resolved and mapped diff result ready for formatting.
    """
    baseline_path = resolve_source(opts.baseline_uri)
    target_path = resolve_source(opts.target_uri)

    baseline_stack = load_stack(baseline_path)
    target_stack = load_stack(target_path)

    raw_diffs = diff_stacks(baseline_stack, target_stack)
    mapped = map_diffs(raw_diffs, mapping=opts.mapping)

    if opts.changed_only:
        mapped = [d for d in mapped if d.changed]

    return MappedPipelineResult(
        diffs=mapped,
        baseline_uri=opts.baseline_uri,
        target_uri=opts.target_uri,
        mapping_applied=opts.mapping,
    )
