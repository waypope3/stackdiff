"""Tests for stackdiff.differ_stats."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_stats import compute_stats, DiffStats


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="a", baseline="1", target="2"),   # changed
        KeyDiff(key="b", baseline="x", target="x"),   # unchanged
        KeyDiff(key="c", baseline=None, target="y"),  # added
        KeyDiff(key="d", baseline="z", target=None),  # removed
        KeyDiff(key="e", baseline="q", target="q"),   # unchanged
    ]


def test_counts(mixed_diffs):
    s = compute_stats(mixed_diffs)
    assert s.total == 5
    assert s.changed == 1
    assert s.added == 1
    assert s.removed == 1
    assert s.unchanged == 2


def test_change_rate(mixed_diffs):
    s = compute_stats(mixed_diffs)
    assert abs(s.change_rate - 3 / 5) < 1e-9


def test_empty_list():
    s = compute_stats([])
    assert s.total == 0
    assert s.change_rate == 0.0


def test_all_unchanged():
    diffs = [KeyDiff(key=k, baseline="v", target="v") for k in "abc"]
    s = compute_stats(diffs)
    assert s.changed == 0
    assert s.added == 0
    assert s.removed == 0
    assert s.change_rate == 0.0


def test_all_added():
    diffs = [KeyDiff(key=k, baseline=None, target="v") for k in "ab"]
    s = compute_stats(diffs)
    assert s.added == 2
    assert s.change_rate == 1.0


def test_all_removed():
    diffs = [KeyDiff(key=k, baseline="v", target=None) for k in "xyz"]
    s = compute_stats(diffs)
    assert s.removed == 3
    assert s.added == 0
    assert s.changed == 0
    assert s.change_rate == 1.0


def test_as_dict_keys(mixed_diffs):
    d = compute_stats(mixed_diffs).as_dict()
    assert set(d.keys()) == {"total", "changed", "added", "removed", "unchanged", "change_rate"}


def test_str_contains_rate(mixed_diffs):
    s = compute_stats(mixed_diffs)
    assert "change_rate" in str(s)
    assert "%" in str(s)


def test_returns_diff_stats_instance(mixed_diffs):
    assert isinstance(compute_stats(mixed_diffs), DiffStats)
