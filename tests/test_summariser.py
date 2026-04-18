"""Tests for stackdiff.summariser."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.summariser import summarise, DiffSummary


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="a", baseline="1", target="2"),   # changed
        KeyDiff(key="b", baseline=None, target="x"),  # added
        KeyDiff(key="c", baseline="y", target=None),  # removed
        KeyDiff(key="d", baseline="z", target="z"),   # unchanged
        KeyDiff(key="e", baseline="p", target="p"),   # unchanged
    ]


def test_counts(mixed_diffs):
    s = summarise(mixed_diffs)
    assert s.total == 5
    assert s.changed == 1
    assert s.added == 1
    assert s.removed == 1
    assert s.unchanged == 2


def test_has_diff_true(mixed_diffs):
    assert summarise(mixed_diffs).has_diff is True


def test_has_diff_false():
    diffs = [KeyDiff(key="a", baseline="1", target="1")]
    assert summarise(diffs).has_diff is False


def test_empty():
    s = summarise([])
    assert s.total == 0
    assert s.has_diff is False


def test_str_with_diffs(mixed_diffs):
    text = str(summarise(mixed_diffs))
    assert "5 key(s)" in text
    assert "changed" in text
    assert "added" in text
    assert "removed" in text


def test_str_no_diffs():
    diffs = [KeyDiff(key="a", baseline="1", target="1")]
    text = str(summarise(diffs))
    assert "no differences" in text


def test_as_dict(mixed_diffs):
    d = summarise(mixed_diffs).as_dict()
    assert set(d.keys()) == {"total", "changed", "added", "removed", "unchanged"}
    assert d["total"] == 5


def test_only_added():
    diffs = [KeyDiff(key="x", baseline=None, target="v")]
    s = summarise(diffs)
    assert s.added == 1
    assert s.changed == 0
    assert s.removed == 0
