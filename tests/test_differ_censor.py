"""Tests for stackdiff.differ_censor."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_censor import CensoredDiff, _edit_distance, censor_diffs


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _d(key: str, bv, tv) -> KeyDiff:
    return KeyDiff(key=key, baseline_value=bv, target_value=tv)


@pytest.fixture()
def mixed_diffs():
    return [
        _d("VpcId", "vpc-aaa", "vpc-bbb"),          # large change
        _d("Unchanged", "same", "same"),             # no change
        _d("Timestamp", "2024-01-01", "2024-01-02"), # tiny change (1 char)
        _d("Added", None, "new-value"),              # added
        _d("Removed", "old-value", None),            # removed
    ]


# ---------------------------------------------------------------------------
# _edit_distance
# ---------------------------------------------------------------------------

def test_edit_distance_identical():
    assert _edit_distance("abc", "abc") == 0


def test_edit_distance_single_insertion():
    assert _edit_distance("abc", "abcd") == 1


def test_edit_distance_single_substitution():
    assert _edit_distance("abc", "axc") == 1


def test_edit_distance_empty_strings():
    assert _edit_distance("", "") == 0


def test_edit_distance_one_empty():
    assert _edit_distance("", "abc") == 3


# ---------------------------------------------------------------------------
# censor_diffs — basic
# ---------------------------------------------------------------------------

def test_returns_censored_diff_instances(mixed_diffs):
    result = censor_diffs(mixed_diffs)
    assert all(isinstance(r, CensoredDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    assert len(censor_diffs(mixed_diffs)) == len(mixed_diffs)


def test_unchanged_key_not_censored(mixed_diffs):
    result = {r.key: r for r in censor_diffs(mixed_diffs)}
    r = result["Unchanged"]
    assert not r.changed
    assert not r.censored
    assert r.reason is None


def test_large_change_not_censored(mixed_diffs):
    result = {r.key: r for r in censor_diffs(mixed_diffs, min_edit_distance=2)}
    r = result["VpcId"]
    assert r.changed
    assert not r.censored


def test_tiny_change_censored_below_threshold(mixed_diffs):
    # "2024-01-01" -> "2024-01-02" is edit distance 1, threshold 2
    result = {r.key: r for r in censor_diffs(mixed_diffs, min_edit_distance=2)}
    r = result["Timestamp"]
    assert not r.changed
    assert r.censored
    assert r.reason is not None


def test_tiny_change_not_censored_when_threshold_is_one(mixed_diffs):
    result = {r.key: r for r in censor_diffs(mixed_diffs, min_edit_distance=1)}
    r = result["Timestamp"]
    assert r.changed
    assert not r.censored


# ---------------------------------------------------------------------------
# censor_diffs — pattern-based censoring
# ---------------------------------------------------------------------------

def test_pattern_censor_suppresses_change():
    diffs = [_d("DeployTimestamp", "v1", "v2")]
    result = censor_diffs(diffs, min_edit_distance=1, censor_patterns=["*Timestamp*"])
    assert result[0].censored
    assert not result[0].changed
    assert "censor pattern" in (result[0].reason or "")


def test_pattern_does_not_affect_non_matching_key():
    diffs = [_d("VpcId", "old", "new")]
    result = censor_diffs(diffs, min_edit_distance=1, censor_patterns=["*Timestamp*"])
    assert not result[0].censored
    assert result[0].changed


# ---------------------------------------------------------------------------
# as_dict / __str__
# ---------------------------------------------------------------------------

def test_as_dict_keys():
    diffs = [_d("Key", "a", "b")]
    d = censor_diffs(diffs, min_edit_distance=1)[0]
    keys = set(d.as_dict().keys())
    assert keys == {"key", "baseline_value", "target_value", "changed", "censored", "reason"}


def test_str_censored_marker():
    diffs = [_d("Ts", "2024-01-01", "2024-01-02")]
    d = censor_diffs(diffs, min_edit_distance=2)[0]
    assert str(d).startswith("[~]")


def test_str_changed_marker():
    diffs = [_d("VpcId", "vpc-aaa", "vpc-bbb")]
    d = censor_diffs(diffs, min_edit_distance=2)[0]
    assert str(d).startswith("[*]")


def test_str_unchanged_marker():
    diffs = [_d("Same", "x", "x")]
    d = censor_diffs(diffs)[0]
    assert str(d).startswith("[ ]")
