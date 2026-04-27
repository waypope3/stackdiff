"""Tests for stackdiff.differ_streaker."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_streaker import StreakedDiff, streak_diffs


def _d(key: str, base: str, target: str) -> KeyDiff:
    return KeyDiff(key=key, baseline_value=base, target_value=target)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def current_diffs():
    return [
        _d("VpcId", "vpc-old", "vpc-new"),       # changed
        _d("Region", "us-east-1", "us-east-1"),  # unchanged
        _d("DbEndpoint", "db-a", "db-b"),         # changed
    ]


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_returns_streaked_diff_instances(current_diffs):
    result = streak_diffs(current_diffs, [])
    assert all(isinstance(r, StreakedDiff) for r in result)


def test_same_length_as_input(current_diffs):
    result = streak_diffs(current_diffs, [])
    assert len(result) == len(current_diffs)


def test_changed_flag_set_when_values_differ(current_diffs):
    result = streak_diffs(current_diffs, [])
    changed_keys = {r.key for r in result if r.changed}
    assert "VpcId" in changed_keys
    assert "DbEndpoint" in changed_keys


def test_changed_flag_clear_when_values_equal(current_diffs):
    result = streak_diffs(current_diffs, [])
    unchanged = [r for r in result if r.key == "Region"]
    assert unchanged[0].changed is False


# ---------------------------------------------------------------------------
# Streak counting
# ---------------------------------------------------------------------------

def test_no_history_streak_one_for_changed(current_diffs):
    result = streak_diffs(current_diffs, [])
    vpc = next(r for r in result if r.key == "VpcId")
    assert vpc.streak == 1


def test_no_history_streak_zero_for_unchanged(current_diffs):
    result = streak_diffs(current_diffs, [])
    region = next(r for r in result if r.key == "Region")
    assert region.streak == 0


def test_streak_increments_with_history(current_diffs):
    history_round = [_d("VpcId", "vpc-prev", "vpc-old")]  # also changed
    result = streak_diffs(current_diffs, [history_round])
    vpc = next(r for r in result if r.key == "VpcId")
    assert vpc.streak == 2


def test_streak_resets_on_gap(current_diffs):
    # round 1: unchanged, round 2: changed — streak should be 1
    round1 = [_d("VpcId", "vpc-same", "vpc-same")]
    round2 = [_d("VpcId", "vpc-same", "vpc-old")]
    result = streak_diffs(current_diffs, [round1, round2])
    vpc = next(r for r in result if r.key == "VpcId")
    # current is changed; round2 is changed; round1 is NOT changed -> streak=2
    assert vpc.streak == 2


# ---------------------------------------------------------------------------
# always_changed flag
# ---------------------------------------------------------------------------

def test_always_changed_true_when_changed_every_round():
    history = [[_d("VpcId", "a", "b")]]
    current = [_d("VpcId", "b", "c")]
    result = streak_diffs(current, history)
    assert result[0].always_changed is True


def test_always_changed_false_when_not_changed_every_round():
    history = [[_d("VpcId", "a", "a")]]  # unchanged in history
    current = [_d("VpcId", "a", "b")]   # changed now
    result = streak_diffs(current, history)
    assert result[0].always_changed is False


def test_always_changed_false_for_unchanged_key():
    current = [_d("Region", "us-east-1", "us-east-1")]
    result = streak_diffs(current, [])
    assert result[0].always_changed is False


# ---------------------------------------------------------------------------
# as_dict
# ---------------------------------------------------------------------------

def test_as_dict_contains_expected_keys(current_diffs):
    result = streak_diffs(current_diffs, [])
    d = result[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "changed", "streak", "always_changed"}
