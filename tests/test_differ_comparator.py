"""Tests for stackdiff.differ_comparator."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_comparator import ComparedDiff, compare_diffs, _shared_prefix, _magnitude


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _d(key: str, bv, tv) -> KeyDiff:
    return KeyDiff(key=key, baseline_value=bv, target_value=tv)


@pytest.fixture()
def mixed_diffs():
    return [
        _d("VpcId", "vpc-aaa", "vpc-bbb"),          # changed, minor
        _d("Region", "us-east-1", "us-east-1"),      # unchanged
        _d("DbEndpoint", None, "db.example.com"),    # added
        _d("OldKey", "legacy-value", None),          # removed
        _d("Arn", "arn:aws:iam::111", "arn:aws:s3:::"),  # changed, major
    ]


# ---------------------------------------------------------------------------
# _shared_prefix
# ---------------------------------------------------------------------------

def test_shared_prefix_common_start():
    assert _shared_prefix("vpc-aaa", "vpc-bbb") == "vpc-"


def test_shared_prefix_no_common():
    assert _shared_prefix("abc", "xyz") == ""


def test_shared_prefix_identical():
    assert _shared_prefix("same", "same") == "same"


def test_shared_prefix_empty_strings():
    assert _shared_prefix("", "") == ""


# ---------------------------------------------------------------------------
# _magnitude
# ---------------------------------------------------------------------------

def test_magnitude_none_when_equal():
    assert _magnitude("x", "x") == "none"


def test_magnitude_added_when_baseline_none():
    assert _magnitude(None, "value") == "added"


def test_magnitude_removed_when_target_none():
    assert _magnitude("value", None) == "removed"


def test_magnitude_minor_for_similar_strings():
    assert _magnitude("vpc-aaa111", "vpc-aaa222") == "minor"


def test_magnitude_major_for_dissimilar_strings():
    assert _magnitude("arn:aws:iam::111", "arn:aws:s3:::") == "major"


# ---------------------------------------------------------------------------
# compare_diffs
# ---------------------------------------------------------------------------

def test_returns_compared_diff_instances(mixed_diffs):
    result = compare_diffs(mixed_diffs)
    assert all(isinstance(r, ComparedDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    assert len(compare_diffs(mixed_diffs)) == len(mixed_diffs)


def test_changed_flag_set_for_different_values(mixed_diffs):
    result = compare_diffs(mixed_diffs)
    changed = {r.key: r.changed for r in result}
    assert changed["VpcId"] is True
    assert changed["Region"] is False
    assert changed["DbEndpoint"] is True
    assert changed["OldKey"] is True


def test_magnitude_assigned_correctly(mixed_diffs):
    result = {r.key: r.magnitude for r in compare_diffs(mixed_diffs)}
    assert result["Region"] == "none"
    assert result["DbEndpoint"] == "added"
    assert result["OldKey"] == "removed"


def test_shared_prefix_populated(mixed_diffs):
    result = {r.key: r.shared_prefix for r in compare_diffs(mixed_diffs)}
    assert result["VpcId"] == "vpc-"
    assert result["Region"] == "us-east-1"


def test_as_dict_keys(mixed_diffs):
    r = compare_diffs(mixed_diffs)[0]
    d = r.as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "changed", "magnitude", "shared_prefix"}


def test_str_changed_marker(mixed_diffs):
    r = compare_diffs(mixed_diffs)[0]  # VpcId changed
    assert str(r).startswith("[~]")


def test_str_unchanged_marker(mixed_diffs):
    r = compare_diffs(mixed_diffs)[1]  # Region unchanged
    assert str(r).startswith("[=]")


def test_empty_list():
    assert compare_diffs([]) == []
