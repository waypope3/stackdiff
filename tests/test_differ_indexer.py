"""Tests for stackdiff.differ_indexer."""
import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_indexer import (
    DiffIndex,
    IndexedDiff,
    _status,
    index_diffs,
)


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="VpcId", baseline_value="vpc-old", target_value="vpc-new"),
        KeyDiff(key="SubnetId", baseline_value="sub-1", target_value="sub-1"),
        KeyDiff(key="BucketName", baseline_value=None, target_value="my-bucket"),
        KeyDiff(key="OldKey", baseline_value="gone", target_value=None),
    ]


def test_returns_diff_index(mixed_diffs):
    result = index_diffs(mixed_diffs)
    assert isinstance(result, DiffIndex)


def test_ordered_length_matches_input(mixed_diffs):
    result = index_diffs(mixed_diffs)
    assert len(result) == len(mixed_diffs)


def test_index_positions_are_sequential(mixed_diffs):
    result = index_diffs(mixed_diffs)
    for i, entry in enumerate(result.ordered):
        assert entry.index == i


def test_lookup_existing_key(mixed_diffs):
    result = index_diffs(mixed_diffs)
    entry = result.lookup("VpcId")
    assert entry is not None
    assert entry.key == "VpcId"


def test_lookup_missing_key(mixed_diffs):
    result = index_diffs(mixed_diffs)
    assert result.lookup("NonExistent") is None


def test_status_changed(mixed_diffs):
    result = index_diffs(mixed_diffs)
    assert result.lookup("VpcId").status == "changed"


def test_status_unchanged(mixed_diffs):
    result = index_diffs(mixed_diffs)
    assert result.lookup("SubnetId").status == "unchanged"


def test_status_added(mixed_diffs):
    result = index_diffs(mixed_diffs)
    assert result.lookup("BucketName").status == "added"


def test_status_removed(mixed_diffs):
    result = index_diffs(mixed_diffs)
    assert result.lookup("OldKey").status == "removed"


def test_by_status_changed(mixed_diffs):
    result = index_diffs(mixed_diffs)
    changed = result.with_status("changed")
    assert len(changed) == 1
    assert changed[0].key == "VpcId"


def test_by_status_added(mixed_diffs):
    result = index_diffs(mixed_diffs)
    added = result.with_status("added")
    assert len(added) == 1
    assert added[0].key == "BucketName"


def test_by_status_missing_returns_empty(mixed_diffs):
    result = index_diffs(mixed_diffs)
    assert result.with_status("nonexistent") == []


def test_changed_flag_set_for_different_values(mixed_diffs):
    result = index_diffs(mixed_diffs)
    assert result.lookup("VpcId").changed is True


def test_changed_flag_clear_for_same_values(mixed_diffs):
    result = index_diffs(mixed_diffs)
    assert result.lookup("SubnetId").changed is False


def test_as_dict_has_expected_keys(mixed_diffs):
    result = index_diffs(mixed_diffs)
    d = result.lookup("VpcId").as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "changed", "index", "status"}


def test_empty_input_returns_empty_index():
    result = index_diffs([])
    assert len(result) == 0
    assert result.ordered == []
