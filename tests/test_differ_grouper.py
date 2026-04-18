"""Tests for stackdiff.differ_grouper."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_grouper import GroupedDiffs, group_diffs


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="a", baseline="1", current="2"),   # changed
        KeyDiff(key="b", baseline="x", current="x"),   # unchanged
        KeyDiff(key="c", baseline=None, current="y"),  # added
        KeyDiff(key="d", baseline="z", current=None),  # removed
        KeyDiff(key="e", baseline="p", current="q"),   # changed
    ]


def test_changed_group(mixed_diffs):
    result = group_diffs(mixed_diffs)
    assert [d.key for d in result.changed] == ["a", "e"]


def test_added_group(mixed_diffs):
    result = group_diffs(mixed_diffs)
    assert [d.key for d in result.added] == ["c"]


def test_removed_group(mixed_diffs):
    result = group_diffs(mixed_diffs)
    assert [d.key for d in result.removed] == ["d"]


def test_unchanged_group(mixed_diffs):
    result = group_diffs(mixed_diffs)
    assert [d.key for d in result.unchanged] == ["b"]


def test_total(mixed_diffs):
    result = group_diffs(mixed_diffs)
    assert result.total() == len(mixed_diffs)


def test_empty_list():
    result = group_diffs([])
    assert result.total() == 0
    assert result.changed == []
    assert result.added == []
    assert result.removed == []
    assert result.unchanged == []


def test_as_dict_keys(mixed_diffs):
    d = group_diffs(mixed_diffs).as_dict()
    assert set(d.keys()) == {"changed", "added", "removed", "unchanged"}


def test_str_repr(mixed_diffs):
    s = str(group_diffs(mixed_diffs))
    assert "changed=2" in s
    assert "added=1" in s
    assert "removed=1" in s
    assert "unchanged=1" in s


def test_all_unchanged():
    diffs = [KeyDiff(key=k, baseline="v", current="v") for k in "abc"]
    result = group_diffs(diffs)
    assert len(result.unchanged) == 3
    assert result.changed == [] and result.added == [] and result.removed == []
