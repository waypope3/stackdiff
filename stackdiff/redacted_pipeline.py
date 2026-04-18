"""Thin wrapper around differ_pipeline that applies redaction before returning."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from stackdiff.differ_pipeline import PipelineOptions, PipelineResult, run_diff_pipeline
from stackdiff.redactor import _DEFAULT_PATTERNS, redact_diffs


@dataclass
class RedactedPipelineOptions:
    pipeline: PipelineOptions
    sensitive_patterns: List[str] = field(default_factory=lambda: list(_DEFAULT_PATTERNS))
    redact: bool = True


def run_redacted_pipeline(
    baseline_path: str,
    target_path: str,
    options: Optional[RedactedPipelineOptions] = None,
) -> PipelineResult:
    """Run the diff pipeline and optionally redact sensitive key values."""
    if options is None:
        options = RedactedPipelineOptions(pipeline=PipelineOptions())

    result = run_diff_pipeline(baseline_path, target_path, options.pipeline)

    if not options.redact:
        return result

    redacted = redact_diffs(result.diffs, patterns=options.sensitive_patterns)
    return PipelineResult(
        diffs=redacted,
        baseline_path=result.baseline_path,
        target_path=result.target_path,
    )
