"""Watch mode: poll sources on an interval and report when diffs change."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from stackdiff.differ import diff_stacks, has_diff
from stackdiff.parser import load_stack
from stackdiff.resolver import resolve_source


@dataclass
class WatchOptions:
    baseline_uri: str
    target_uri: str
    interval: int = 30          # seconds between polls
    max_polls: Optional[int] = None  # None = run forever
    on_change: Callable[[list], None] = field(default=lambda diffs: None)
    on_no_change: Callable[[], None] = field(default=lambda: None)


def _fetch_diffs(baseline_uri: str, target_uri: str) -> list:
    baseline_path = resolve_source(baseline_uri)
    target_path = resolve_source(target_uri)
    baseline = load_stack(baseline_path)
    target = load_stack(target_path)
    return diff_stacks(baseline, target)


def watch(options: WatchOptions) -> None:
    """Poll sources and invoke callbacks when diff state changes."""
    last_had_diff: Optional[bool] = None
    polls = 0

    while True:
        diffs = _fetch_diffs(options.baseline_uri, options.target_uri)
        current_has_diff = has_diff(diffs)

        if current_has_diff != last_had_diff:
            if current_has_diff:
                options.on_change(diffs)
            else:
                options.on_no_change()

        last_had_diff = current_has_diff
        polls += 1

        if options.max_polls is not None and polls >= options.max_polls:
            break

        time.sleep(options.interval)
