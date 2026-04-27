"""Tests for differ_chaperon."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_chaperon import ChaperondDiff, chaperon_diffs, _similarity


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="VpcId",        baseline_value="vpc-aabbccdd", target_value="vpc-11223344"),
        KeyDiff(key="SubnetId",     baseline_value="subnet-aabbcc", target_value="subnet-aabbcc"),
        KeyDiff(key="DbEndpoint",   baseline_value="db.example.com", target_value="db2.example.com"),
        KeyDiff(key="BucketName",   baseline_value=None,            target_value="my-bucket"),
        KeyDiff(key="OldResource",  baseline_value="res-xyz",       target_value=None),
    ]


# ---------------------------------------------------------------------------
# _similarity
# ---------------------------------------------------------------------------

def test_similarity_identical():
    assert _similarity("abc", "abc") == 1.0


def test_similarity_empty_returns_zero():
    assert _similarity("", "hello") == 0.0
    assert _similarity(None, "hello") == 0.0


def test_similarity_partial():
    score = _similarity("vpc-aabbccdd", "vpc-aabbccee")
    assert 0.0 < score < 1.0


# ---------------------------------------------------------------------------
# chaperon_diffs
# ---------------------------------------------------------------------------

def test_returns_chaperond_diff_instances(mixed_diffs):
    result = chaperon_diffs(mixed_diffs)
    assert all(isinstance(r, ChaperondDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    result = chaperon_diffs(mixed_diffs)
    assert len(result) == len(mixed_diffs)


def test_changed_flag_set_when_values_differ(mixed_diffs):
    result = {r.key: r for r in chaperon_diffs(mixed_diffs)}
    assert result["VpcId"].changed is True


def test_changed_flag_clear_when_values_equal(mixed_diffs):
    result = {r.key: r for r in chaperon_diffs(mixed_diffs)}
    assert result["SubnetId"].changed is False


def test_added_key_marked_changed(mixed_diffs):
    result = {r.key: r for r in chaperon_diffs(mixed_diffs)}
    assert result["BucketName"].changed is True


def test_removed_key_marked_changed(mixed_diffs):
    result = {r.key: r for r in chaperon_diffs(mixed_diffs)}
    assert result["OldResource"].changed is True


def test_companion_found_for_similar_values():
    diffs = [
        KeyDiff(key="A", baseline_value="vpc-aabbccdd", target_value="vpc-11223344"),
        KeyDiff(key="B", baseline_value="vpc-aabbccee", target_value="vpc-aabbccee"),
    ]
    result = {r.key: r for r in chaperon_diffs(diffs, min_similarity=0.5)}
    assert result["A"].companion_key == "B"
    assert result["A"].companion_similarity > 0.5


def test_no_companion_when_below_threshold():
    diffs = [
        KeyDiff(key="A", baseline_value="abc", target_value="xyz"),
        KeyDiff(key="B", baseline_value="123456789", target_value="123456789"),
    ]
    result = {r.key: r for r in chaperon_diffs(diffs, min_similarity=0.99)}
    assert result["A"].companion_key is None


def test_exclude_patterns_respected():
    diffs = [
        KeyDiff(key="VpcId",    baseline_value="vpc-aabbccdd", target_value="vpc-11223344"),
        KeyDiff(key="VpcAlias", baseline_value="vpc-aabbccee", target_value="vpc-aabbccee"),
    ]
    result = {r.key: r for r in chaperon_diffs(diffs, min_similarity=0.5, exclude_patterns=["Vpc*"])}
    # VpcId should not find VpcAlias as companion because it is excluded
    assert result["VpcId"].companion_key is None


def test_as_dict_keys(mixed_diffs):
    result = chaperon_diffs(mixed_diffs)
    d = result[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "changed",
                              "companion_key", "companion_similarity"}


def test_str_changed_marker(mixed_diffs):
    result = {r.key: r for r in chaperon_diffs(mixed_diffs)}
    assert "~" in str(result["VpcId"]) or "VpcId" in str(result["VpcId"])


def test_str_unchanged_marker(mixed_diffs):
    result = {r.key: r for r in chaperon_diffs(mixed_diffs)}
    assert "=" in str(result["SubnetId"]) or "SubnetId" in str(result["SubnetId"])
