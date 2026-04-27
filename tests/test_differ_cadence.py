"""Tests for stackdiff.differ_cadence."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_cadence import CadencedDiff, cadence_diffs, _stability


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _d(key: str, bv: str, tv: str) -> KeyDiff:
    return KeyDiff(key=key, baseline_value=bv, target_value=tv)


@pytest.fixture()
def history():
    """Three historical snapshots for VpcId, SubnetId, DbEndpoint."""
    snap1 = [_d("VpcId", "vpc-aaa", "vpc-bbb"), _d("SubnetId", "sub-1", "sub-1")]
    snap2 = [_d("VpcId", "vpc-bbb", "vpc-ccc"), _d("SubnetId", "sub-1", "sub-1")]
    snap3 = [_d("VpcId", "vpc-ccc", "vpc-ccc"), _d("SubnetId", "sub-1", "sub-2"),
             _d("DbEndpoint", "db-old", "db-new")]
    return [snap1, snap2, snap3]


@pytest.fixture()
def current():
    return [
        _d("VpcId", "vpc-ccc", "vpc-ddd"),
        _d("SubnetId", "sub-2", "sub-2"),
        _d("DbEndpoint", "db-new", "db-new"),
        _d("NewKey", "", "some-value"),
    ]


# ---------------------------------------------------------------------------
# _stability
# ---------------------------------------------------------------------------

def test_stability_zero_is_stable():
    assert _stability(0.0) == "stable"


def test_stability_low_is_moderate():
    assert _stability(0.3) == "moderate"


def test_stability_high_is_volatile():
    assert _stability(0.8) == "volatile"


def test_stability_boundary_moderate():
    assert _stability(0.4) == "moderate"


# ---------------------------------------------------------------------------
# cadence_diffs
# ---------------------------------------------------------------------------

def test_returns_cadenced_diff_instances(history, current):
    result = cadence_diffs(history, current)
    assert all(isinstance(r, CadencedDiff) for r in result)


def test_same_length_as_current(history, current):
    result = cadence_diffs(history, current)
    assert len(result) == len(current)


def test_volatile_key_detected(history, current):
    result = cadence_diffs(history, current)
    vpc = next(r for r in result if r.key == "VpcId")
    # appeared 3 times, changed twice → cadence = 2/3 ≈ 0.67 → volatile
    assert vpc.appearances == 3
    assert vpc.change_count == 2
    assert vpc.stability == "volatile"


def test_stable_key_detected(history, current):
    result = cadence_diffs(history, current)
    subnet = next(r for r in result if r.key == "SubnetId")
    # appeared 3 times, changed once → cadence = 1/3 ≈ 0.33 → moderate
    assert subnet.stability == "moderate"


def test_key_not_in_history_has_zero_cadence(history, current):
    result = cadence_diffs(history, current)
    new_key = next(r for r in result if r.key == "NewKey")
    assert new_key.appearances == 0
    assert new_key.cadence == 0.0
    assert new_key.stability == "stable"


def test_changed_flag_reflects_current_diff(history, current):
    result = cadence_diffs(history, current)
    vpc = next(r for r in result if r.key == "VpcId")
    subnet = next(r for r in result if r.key == "SubnetId")
    assert vpc.changed is True
    assert subnet.changed is False


def test_empty_history_all_stable():
    current = [_d("Key", "a", "b")]
    result = cadence_diffs([], current)
    assert result[0].cadence == 0.0
    assert result[0].stability == "stable"


def test_as_dict_keys(history, current):
    result = cadence_diffs(history, current)
    d = result[0].as_dict()
    expected = {"key", "baseline_value", "target_value", "changed",
                "appearances", "change_count", "cadence", "stability"}
    assert set(d.keys()) == expected


def test_str_contains_key_and_stability(history, current):
    result = cadence_diffs(history, current)
    s = str(result[0])
    assert "VpcId" in s
    assert "volatile" in s
