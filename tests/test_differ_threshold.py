"""Tests for differ_threshold and threshold_formatter."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_threshold import (
    ThresholdOptions,
    ThresholdedDiff,
    _edit_distance,
    apply_threshold,
)
from stackdiff.threshold_formatter import format_thresholded


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _d(key: str, baseline: str | None, target: str | None) -> KeyDiff:
    return KeyDiff(key=key, baseline_value=baseline, target_value=target, changed=baseline != target)


@pytest.fixture()
def mixed_diffs() -> list[KeyDiff]:
    return [
        _d("Unchanged", "same", "same"),
        _d("SmallChange", "hello", "helo"),   # edit distance 1
        _d("BigChange", "foo", "barbazqux"),  # edit distance 8
        _d("Added", None, "new-value"),
        _d("Removed", "old-value", None),
    ]


# ---------------------------------------------------------------------------
# _edit_distance
# ---------------------------------------------------------------------------

def test_edit_distance_identical():
    assert _edit_distance("abc", "abc") == 0


def test_edit_distance_insertion():
    assert _edit_distance("abc", "abcd") == 1


def test_edit_distance_substitution():
    assert _edit_distance("abc", "axc") == 1


def test_edit_distance_none_values():
    assert _edit_distance(None, "hello") == 5
    assert _edit_distance("hello", None) == 5
    assert _edit_distance(None, None) == 0


# ---------------------------------------------------------------------------
# apply_threshold
# ---------------------------------------------------------------------------

def test_returns_thresholded_diff_instances(mixed_diffs):
    result = apply_threshold(mixed_diffs)
    assert all(isinstance(r, ThresholdedDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    assert len(apply_threshold(mixed_diffs)) == len(mixed_diffs)


def test_no_threshold_nothing_suppressed(mixed_diffs):
    result = apply_threshold(mixed_diffs, ThresholdOptions(min_edit_distance=0))
    assert not any(r.suppressed for r in result)


def test_small_change_suppressed_below_threshold(mixed_diffs):
    result = apply_threshold(mixed_diffs, ThresholdOptions(min_edit_distance=3))
    by_key = {r.key: r for r in result}
    assert by_key["SmallChange"].suppressed is True
    assert by_key["BigChange"].suppressed is False


def test_unchanged_never_suppressed(mixed_diffs):
    result = apply_threshold(mixed_diffs, ThresholdOptions(min_edit_distance=100))
    by_key = {r.key: r for r in result}
    assert by_key["Unchanged"].suppressed is False


def test_structural_kept_when_flag_true(mixed_diffs):
    opts = ThresholdOptions(min_edit_distance=100, keep_structural=True)
    result = apply_threshold(mixed_diffs, opts)
    by_key = {r.key: r for r in result}
    assert by_key["Added"].suppressed is False
    assert by_key["Removed"].suppressed is False


def test_structural_suppressed_when_flag_false(mixed_diffs):
    opts = ThresholdOptions(min_edit_distance=100, keep_structural=False)
    result = apply_threshold(mixed_diffs, opts)
    by_key = {r.key: r for r in result}
    assert by_key["Added"].suppressed is True
    assert by_key["Removed"].suppressed is True


def test_as_dict_keys(mixed_diffs):
    item = apply_threshold(mixed_diffs)[0]
    d = item.as_dict()
    assert set(d) == {"key", "baseline_value", "target_value", "changed", "edit_distance", "suppressed"}


# ---------------------------------------------------------------------------
# format_thresholded
# ---------------------------------------------------------------------------

def test_format_contains_key(mixed_diffs):
    result = apply_threshold(mixed_diffs)
    output = format_thresholded(result)
    assert "BigChange" in output


def test_format_hides_suppressed_by_default(mixed_diffs):
    opts = ThresholdOptions(min_edit_distance=3)
    result = apply_threshold(mixed_diffs, opts)
    output = format_thresholded(result)
    assert "SmallChange" not in output
    assert "suppressed by threshold" in output


def test_format_shows_suppressed_when_requested(mixed_diffs):
    opts = ThresholdOptions(min_edit_distance=3)
    result = apply_threshold(mixed_diffs, opts)
    output = format_thresholded(result, show_suppressed=True)
    assert "SmallChange" in output
