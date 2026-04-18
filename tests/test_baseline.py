"""Tests for stackdiff.baseline."""
from __future__ import annotations

import json
import pytest

from stackdiff.baseline import compare_to_baseline, update_baseline, BaselineError


@pytest.fixture()
def snap_dir(tmp_path):
    d = tmp_path / "snaps"
    d.mkdir()
    return str(d)


@pytest.fixture()
def saved_baseline(snap_dir):
    stack = {"KeyA": "val1", "KeyB": "val2"}
    update_baseline(stack, "prod", snap_dir=snap_dir)
    return stack


def test_compare_no_diff(snap_dir, saved_baseline):
    result = compare_to_baseline(saved_baseline, "prod", snap_dir=snap_dir)
    assert not result.summary.has_diff()
    assert result.snapshot_name == "prod"


def test_compare_detects_change(snap_dir, saved_baseline):
    changed = {"KeyA": "NEW", "KeyB": "val2"}
    result = compare_to_baseline(changed, "prod", snap_dir=snap_dir)
    assert result.summary.has_diff()
    assert result.summary.changed == 1


def test_compare_detects_added(snap_dir, saved_baseline):
    extended = {**saved_baseline, "KeyC": "extra"}
    result = compare_to_baseline(extended, "prod", snap_dir=snap_dir)
    assert result.summary.added == 1


def test_compare_detects_removed(snap_dir, saved_baseline):
    reduced = {"KeyA": "val1"}
    result = compare_to_baseline(reduced, "prod", snap_dir=snap_dir)
    assert result.summary.removed == 1


def test_missing_baseline_raises(snap_dir):
    with pytest.raises(BaselineError, match="Cannot load baseline"):
        compare_to_baseline({}, "nonexistent", snap_dir=snap_dir)


def test_update_creates_file(snap_dir):
    path = update_baseline({"X": "1"}, "staging", snap_dir=snap_dir)
    assert path
    import os
    assert os.path.exists(path)


def test_update_overwrites(snap_dir):
    update_baseline({"X": "1"}, "env", snap_dir=snap_dir)
    update_baseline({"X": "2"}, "env", snap_dir=snap_dir)
    result = compare_to_baseline({"X": "2"}, "env", snap_dir=snap_dir)
    assert not result.summary.has_diff()
