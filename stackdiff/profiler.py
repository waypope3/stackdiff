"""Timing profiler for stackdiff pipeline stages."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Span:
    name: str
    elapsed: float  # seconds


@dataclass
class Profile:
    spans: List[Span] = field(default_factory=list)

    def record(self, name: str, elapsed: float) -> None:
        self.spans.append(Span(name=name, elapsed=elapsed))

    def total(self) -> float:
        return sum(s.elapsed for s in self.spans)

    def summary(self) -> Dict[str, float]:
        return {s.name: round(s.elapsed, 4) for s in self.spans}

    def slowest(self) -> Optional[Span]:
        if not self.spans:
            return None
        return max(self.spans, key=lambda s: s.elapsed)


class Profiler:
    """Context-manager based profiler that accumulates spans into a Profile."""

    def __init__(self) -> None:
        self._profile = Profile()
        self._current: Optional[str] = None
        self._start: Optional[float] = None

    def start(self, name: str) -> None:
        self._current = name
        self._start = time.perf_counter()

    def stop(self) -> None:
        if self._current is None or self._start is None:
            raise RuntimeError("stop() called without a matching start()")
        elapsed = time.perf_counter() - self._start
        self._profile.record(self._current, elapsed)
        self._current = None
        self._start = None

    def stage(self, name: str):
        """Return a context manager for a named stage."""
        profiler = self

        class _Stage:
            def __enter__(self_):
                profiler.start(name)
                return self_

            def __exit__(self_, *_):
                profiler.stop()

        return _Stage()

    @property
    def profile(self) -> Profile:
        return self._profile
