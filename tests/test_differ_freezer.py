"""Tests for stackdiff.differ_freezer."""
import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_freezer import FrozenDiff, freeze_diffs, _matches_freeze


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _d(key: str, baseline: str = "a", target: str = "a") -> KeyDiff:
    return KeyDiff(key=key, baseline_value=baseline, target_value=target)


@pytest.fixture()
def mixed_diffs() -> list:
    return [
        _d("VpcId", "vpc-111", "vpc-222"),       # changed
        _d("SubnetId", "sub-1", "sub-1"),         # unchanged
        _d("DbEndpoint", "old.db", "new.db"),     # changed
        _d("BucketName", "my-bucket", "my-bucket"),  # unchanged
    ]


# ---------------------------------------------------------------------------
# _matches_freeze
# ---------------------------------------------------------------------------

def test_matches_freeze_exact():
    assert _matches_freeze("VpcId", ["VpcId"]) == "VpcId"


def test_matches_freeze_glob():
    assert _matches_freeze("DbEndpoint", ["Db*"]) == "Db*"


def test_matches_freeze_no_match():
    assert _matches_freeze("VpcId", ["Db*"]) is None


def test_matches_freeze_first_pattern_wins():
    result = _matches_freeze("VpcId", ["Vpc*", "VpcId"])
    assert result == "Vpc*"


# ---------------------------------------------------------------------------
# freeze_diffs – basic structure
# ---------------------------------------------------------------------------

def test_returns_frozen_diff_instances(mixed_diffs):
    result = freeze_diffs(mixed_diffs)
    assert all(isinstance(d, FrozenDiff) for d in result)


def test_same_length_as_input(mixed_diffs):
    assert len(freeze_diffs(mixed_diffs)) == len(mixed_diffs)


def test_no_patterns_nothing_frozen(mixed_diffs):
    result = freeze_diffs(mixed_diffs, freeze_patterns=[])
    assert all(not d.frozen for d in result)


def test_no_patterns_freeze_pattern_is_none(mixed_diffs):
    result = freeze_diffs(mixed_diffs)
    assert all(d.freeze_pattern is None for d in result)


# ---------------------------------------------------------------------------
# changed flag
# ---------------------------------------------------------------------------

def test_changed_flag_set_when_values_differ(mixed_diffs):
    result = freeze_diffs(mixed_diffs)
    assert result[0].changed is True   # VpcId differs


def test_changed_flag_clear_when_values_equal(mixed_diffs):
    result = freeze_diffs(mixed_diffs)
    assert result[1].changed is False  # SubnetId same


# ---------------------------------------------------------------------------
# frozen flag
# ---------------------------------------------------------------------------

def test_frozen_flag_set_for_matching_key(mixed_diffs):
    result = freeze_diffs(mixed_diffs, freeze_patterns=["VpcId"])
    assert result[0].frozen is True


def test_frozen_flag_clear_for_non_matching_key(mixed_diffs):
    result = freeze_diffs(mixed_diffs, freeze_patterns=["VpcId"])
    assert result[1].frozen is False


def test_frozen_glob_matches_multiple(mixed_diffs):
    result = freeze_diffs(mixed_diffs, freeze_patterns=["*Id"])
    frozen_keys = {d.key for d in result if d.frozen}
    assert frozen_keys == {"VpcId", "SubnetId"}


def test_freeze_pattern_recorded(mixed_diffs):
    result = freeze_diffs(mixed_diffs, freeze_patterns=["Db*"])
    db = next(d for d in result if d.key == "DbEndpoint")
    assert db.freeze_pattern == "Db*"


# ---------------------------------------------------------------------------
# as_dict
# ---------------------------------------------------------------------------

def test_as_dict_keys(mixed_diffs):
    d = freeze_diffs(mixed_diffs)[0]
    keys = set(d.as_dict())
    assert keys == {"key", "baseline_value", "target_value", "changed", "frozen", "freeze_pattern"}


def test_as_dict_values_match_attributes(mixed_diffs):
    result = freeze_diffs(mixed_diffs, freeze_patterns=["VpcId"])
    d = result[0]
    data = d.as_dict()
    assert data["key"] == d.key
    assert data["frozen"] == d.frozen
    assert data["changed"] == d.changed
