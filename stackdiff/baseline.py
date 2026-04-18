"""Baseline comparison: compare a stack against a saved snapshot."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from stackdiff.snapshot import load_snapshot, save_snapshot, SnapshotError
from stackdiff.differ import diff_stacks, KeyDiff
from stackdiff.summariser import summarise, DiffSummary


@dataclass
class BaselineResult:
    snapshot_name: str
    diffs: list[KeyDiff]
    summary: DiffSummary


class BaselineError(Exception):
    pass


def compare_to_baseline(
    stack: dict,
    snapshot_name: str,
    snap_dir: str = ".stackdiff/snapshots",
) -> BaselineResult:
    """Diff *stack* against a previously saved snapshot."""
    try:
        baseline = load_snapshot(snapshot_name, snap_dir=snap_dir)
    except SnapshotError as exc:
        raise BaselineError(f"Cannot load baseline '{snapshot_name}': {exc}") from exc

    diffs = diff_stacks(baseline, stack)
    return BaselineResult(
        snapshot_name=snapshot_name,
        diffs=diffs,
        summary=summarise(diffs),
    )


def update_baseline(
    stack: dict,
    snapshot_name: str,
    snap_dir: str = ".stackdiff/snapshots",
) -> str:
    """Save *stack* as the new baseline snapshot, return the path."""
    from stackdiff.differ import KeyDiff  # noqa: F401 – ensure differ loaded
    path = save_snapshot(stack, snapshot_name, snap_dir=snap_dir)
    return path
