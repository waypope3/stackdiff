"""Tests for stackdiff.differ_watch."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from stackdiff.differ_watch import WatchOptions, watch


@pytest.fixture()
def stack_files(tmp_path: Path):
    baseline = tmp_path / "baseline.json"
    target = tmp_path / "target.json"
    baseline.write_text(json.dumps({"Outputs": {"Key": "value_a"}}))
    target.write_text(json.dumps({"Outputs": {"Key": "value_a"}}))
    return baseline, target


def _make_opts(baseline, target, on_change=None, on_no_change=None, max_polls=1):
    return WatchOptions(
        baseline_uri=str(baseline),
        target_uri=str(target),
        interval=0,
        max_polls=max_polls,
        on_change=on_change or MagicMock(),
        on_no_change=on_no_change or MagicMock(),
    )


def test_no_diff_calls_on_no_change(stack_files):
    baseline, target = stack_files
    on_change = MagicMock()
    on_no_change = MagicMock()
    opts = _make_opts(baseline, target, on_change=on_change, on_no_change=on_no_change)
    watch(opts)
    on_no_change.assert_called_once()
    on_change.assert_not_called()


def test_diff_calls_on_change(stack_files, tmp_path):
    baseline, _ = stack_files
    target = tmp_path / "target2.json"
    target.write_text(json.dumps({"Outputs": {"Key": "value_b"}}))
    on_change = MagicMock()
    on_no_change = MagicMock()
    opts = _make_opts(baseline, target, on_change=on_change, on_no_change=on_no_change)
    watch(opts)
    on_change.assert_called_once()
    on_no_change.assert_not_called()


def test_on_change_receives_diffs(stack_files, tmp_path):
    baseline, _ = stack_files
    target = tmp_path / "target3.json"
    target.write_text(json.dumps({"Outputs": {"Key": "value_b"}}))
    captured = []
    opts = _make_opts(baseline, target, on_change=lambda d: captured.extend(d))
    watch(opts)
    assert len(captured) == 1
    assert captured[0].key == "Key"


def test_max_polls_respected(stack_files):
    baseline, target = stack_files
    on_no_change = MagicMock()
    opts = _make_opts(baseline, target, on_no_change=on_no_change, max_polls=3)
    watch(opts)
    # on_no_change called only on first poll (state change from None -> False)
    assert on_no_change.call_count == 1


def test_sleep_called_between_polls(stack_files):
    baseline, target = stack_files
    opts = WatchOptions(
        baseline_uri=str(baseline),
        target_uri=str(target),
        interval=5,
        max_polls=2,
    )
    with patch("stackdiff.differ_watch.time.sleep") as mock_sleep:
        watch(opts)
    assert mock_sleep.call_count == 1
    mock_sleep.assert_called_with(5)
