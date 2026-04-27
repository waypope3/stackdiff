"""Tests for stackdiff.differ_correlator."""
from __future__ import annotations

import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_correlator import CorrelatedDiff, correlate_diffs, _changed_keys


@pytest.fixture()
def primary():
    return [
        KeyDiff(key="VpcId", baseline="vpc-aaa", target="vpc-bbb"),
        KeyDiff(key="SubnetId", baseline="subnet-111", target="subnet-222"),
        KeyDiff(key="Region", baseline="us-east-1", target="us-east-1"),
    ]


@pytest.fixture()
def history():
    # Two historical comparisons where VpcId and SubnetId always change together
    snap1 = [
        KeyDiff(key="VpcId", baseline="vpc-000", target="vpc-aaa"),
        KeyDiff(key="SubnetId", baseline="subnet-000", target="subnet-111"),
        KeyDiff(key="Region", baseline="us-east-1", target="us-east-1"),
    ]
    snap2 = [
        KeyDiff(key="VpcId", baseline="vpc-x", target="vpc-y"),
        KeyDiff(key="SubnetId", baseline="subnet-x", target="subnet-y"),
    ]
    return [snap1, snap2]


def test_returns_correlated_diff_instances(primary, history):
    result = correlate_diffs(primary, history)
    assert all(isinstance(d, CorrelatedDiff) for d in result)


def test_same_length_as_input(primary, history):
    result = correlate_diffs(primary, history)
    assert len(result) == len(primary)


def test_changed_flag_set_for_different_values(primary, history):
    result = correlate_diffs(primary, history)
    by_key = {d.key: d for d in result}
    assert by_key["VpcId"].changed is True
    assert by_key["SubnetId"].changed is True


def test_unchanged_flag_clear_for_equal_values(primary, history):
    result = correlate_diffs(primary, history)
    by_key = {d.key: d for d in result}
    assert by_key["Region"].changed is False


def test_co_changed_populated_for_correlated_keys(primary, history):
    result = correlate_diffs(primary, history)
    by_key = {d.key: d for d in result}
    assert "SubnetId" in by_key["VpcId"].co_changed_with


def test_correlation_score_positive_for_correlated_keys(primary, history):
    result = correlate_diffs(primary, history)
    by_key = {d.key: d for d in result}
    assert by_key["VpcId"].correlation_score > 0.0


def test_unchanged_key_has_zero_score(primary, history):
    result = correlate_diffs(primary, history)
    by_key = {d.key: d for d in result}
    assert by_key["Region"].correlation_score == 0.0


def test_no_history_gives_no_co_changes(primary):
    result = correlate_diffs(primary, [])
    for d in result:
        assert d.co_changed_with == []
        assert d.correlation_score == 0.0


def test_changed_keys_helper():
    diffs = [
        KeyDiff(key="A", baseline="x", target="y"),
        KeyDiff(key="B", baseline="z", target="z"),
    ]
    assert _changed_keys(diffs) == frozenset({"A"})


def test_as_dict_contains_expected_keys(primary, history):
    result = correlate_diffs(primary, history)
    d = result[0].as_dict()
    assert set(d.keys()) == {
        "key", "baseline_value", "target_value",
        "changed", "co_changed_with", "correlation_score",
    }


def test_str_representation(primary, history):
    result = correlate_diffs(primary, history)
    for d in result:
        assert d.key in str(d)
