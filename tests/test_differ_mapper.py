"""Tests for stackdiff.differ_mapper."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_mapper import MappedDiff, map_diffs


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="VpcId", baseline_value="vpc-111", target_value="vpc-222"),
        KeyDiff(key="SubnetId", baseline_value="subnet-aaa", target_value="subnet-aaa"),
        KeyDiff(key="DbEndpoint", baseline_value=None, target_value="db.example.com"),
        KeyDiff(key="OldBucket", baseline_value="my-bucket", target_value=None),
    ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_returns_mapped_diff_instances(mixed_diffs):
    result = map_diffs(mixed_diffs, mapping={})
    assert all(isinstance(r, MappedDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    result = map_diffs(mixed_diffs, mapping={})
    assert len(result) == len(mixed_diffs)


def test_no_mapping_key_unchanged(mixed_diffs):
    result = map_diffs(mixed_diffs, mapping={})
    for r, d in zip(result, mixed_diffs):
        assert r.mapped_key == d.key
        assert not r.was_remapped


def test_mapped_key_applied():
    diffs = [KeyDiff(key="VpcId", baseline_value="a", target_value="b")]
    result = map_diffs(diffs, mapping={"VpcId": "Virtual Private Cloud ID"})
    assert result[0].mapped_key == "Virtual Private Cloud ID"
    assert result[0].was_remapped is True


def test_original_key_preserved_after_remap():
    diffs = [KeyDiff(key="VpcId", baseline_value="a", target_value="b")]
    result = map_diffs(diffs, mapping={"VpcId": "Network"})
    assert result[0].original_key == "VpcId"


def test_changed_flag_true_when_values_differ():
    diffs = [KeyDiff(key="VpcId", baseline_value="vpc-111", target_value="vpc-222")]
    result = map_diffs(diffs, mapping={})
    assert result[0].changed is True


def test_changed_flag_false_when_values_equal():
    diffs = [KeyDiff(key="SubnetId", baseline_value="subnet-aaa", target_value="subnet-aaa")]
    result = map_diffs(diffs, mapping={})
    assert result[0].changed is False


def test_added_key_marked_changed():
    diffs = [KeyDiff(key="DbEndpoint", baseline_value=None, target_value="db.example.com")]
    result = map_diffs(diffs, mapping={})
    assert result[0].changed is True


def test_removed_key_marked_changed():
    diffs = [KeyDiff(key="OldBucket", baseline_value="my-bucket", target_value=None)]
    result = map_diffs(diffs, mapping={})
    assert result[0].changed is True


def test_as_dict_keys(mixed_diffs):
    result = map_diffs(mixed_diffs, mapping={})
    d = result[0].as_dict()
    assert set(d.keys()) == {
        "original_key",
        "mapped_key",
        "baseline_value",
        "target_value",
        "changed",
        "was_remapped",
    }


def test_partial_mapping_only_remaps_matched_keys(mixed_diffs):
    mapping = {"VpcId": "Network ID"}
    result = map_diffs(mixed_diffs, mapping=mapping)
    remapped = [r for r in result if r.was_remapped]
    assert len(remapped) == 1
    assert remapped[0].mapped_key == "Network ID"


def test_empty_diffs_returns_empty():
    result = map_diffs([], mapping={"VpcId": "Network"})
    assert result == []
