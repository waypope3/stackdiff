"""Randomly sample a subset of diffs for large stack comparisons."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class SampledDiff:
    """A KeyDiff decorated with sampling metadata."""

    key: str
    baseline_value: Optional[str]
    target_value: Optional[str]
    changed: bool
    included: bool  # False when excluded by sampler
    sample_index: int  # position in the sampled subset; -1 if excluded

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "included": self.included,
            "sample_index": self.sample_index,
        }

    def __str__(self) -> str:  # pragma: no cover
        mark = "*" if self.changed else " "
        inc = "+" if self.included else "-"
        return f"[{inc}][{mark}] {self.key}: {self.baseline_value!r} -> {self.target_value!r}"


@dataclass
class SampleOptions:
    """Controls how sampling is performed."""

    n: int  # maximum number of diffs to include
    seed: Optional[int] = None  # for reproducible sampling
    changed_first: bool = True  # always include changed diffs before sampling unchanged


def sample_diffs(
    diffs: Sequence[KeyDiff],
    options: SampleOptions,
) -> List[SampledDiff]:
    """Return a sampled list of SampledDiff instances.

    When *changed_first* is True, all changed diffs are kept and only
    unchanged diffs are subject to random sampling to fill the remaining
    quota.  When the total number of diffs is within *n*, all are included.
    """
    if options.n < 0:
        raise ValueError("SampleOptions.n must be >= 0")

    rng = random.Random(options.seed)

    changed = [d for d in diffs if d.baseline_value != d.target_value]
    unchanged = [d for d in diffs if d.baseline_value == d.target_value]

    if options.changed_first:
        selected_changed = changed[: options.n]
        remaining_slots = max(0, options.n - len(selected_changed))
        selected_unchanged = rng.sample(
            unchanged, min(remaining_slots, len(unchanged))
        )
        included_keys = {d.key for d in selected_changed + selected_unchanged}
    else:
        pool = list(diffs)
        rng.shuffle(pool)
        included_keys = {d.key for d in pool[: options.n]}

    result: List[SampledDiff] = []
    sample_idx = 0
    for diff in diffs:
        inc = diff.key in included_keys
        result.append(
            SampledDiff(
                key=diff.key,
                baseline_value=diff.baseline_value,
                target_value=diff.target_value,
                changed=diff.baseline_value != diff.target_value,
                included=inc,
                sample_index=sample_idx if inc else -1,
            )
        )
        if inc:
            sample_idx += 1
    return result
