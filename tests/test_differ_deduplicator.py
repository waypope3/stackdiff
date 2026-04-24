"""Tests for stackdiff.differ_deduplicator."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_deduplicator import DeduplicatedDiff, deduplicate_diffs


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _d(key: str, base=None, target=None) -> KeyDiff:
    return KeyDiff(key=key, baseline_value=base, target_value=target)


# ---------------------------------------------------------------------------
# basic behaviour
# ---------------------------------------------------------------------------

def test_empty_list_returns_empty():
    assert deduplicate_diffs([]) == []


def test_no_duplicates_returns_all():
    diffs = [_d("a", "1", "1"), _d("b", "2", "3"), _d("c", None, "x")]
    result = deduplicate_diffs(diffs)
    assert [r.key for r in result] == ["a", "b", "c"]


def test_duplicate_key_last_value_wins():
    diffs = [_d("x", "old", "old"), _d("x", "new", "new2")]
    result = deduplicate_diffs(diffs)
    assert len(result) == 1
    assert result[0].baseline_value == "new"
    assert result[0].target_value == "new2"


def test_duplicate_count_recorded():
    diffs = [_d("k", "a", "a"), _d("k", "b", "b"), _d("k", "c", "c")]
    result = deduplicate_diffs(diffs)
    assert result[0].duplicate_count == 3


def test_non_duplicate_count_is_one():
    result = deduplicate_diffs([_d("solo", "v", "v")])
    assert result[0].duplicate_count == 1


# ---------------------------------------------------------------------------
# changed flag
# ---------------------------------------------------------------------------

def test_changed_flag_true_when_values_differ():
    result = deduplicate_diffs([_d("k", "a", "b")])
    assert result[0].changed is True


def test_changed_flag_false_when_values_equal():
    result = deduplicate_diffs([_d("k", "a", "a")])
    assert result[0].changed is False


def test_changed_flag_true_when_added():
    result = deduplicate_diffs([_d("k", None, "new")])
    assert result[0].changed is True


def test_changed_flag_true_when_removed():
    result = deduplicate_diffs([_d("k", "old", None)])
    assert result[0].changed is True


# ---------------------------------------------------------------------------
# ordering
# ---------------------------------------------------------------------------

def test_first_seen_order_preserved():
    diffs = [_d("b", "1", "1"), _d("a", "2", "2"), _d("b", "3", "3")]
    result = deduplicate_diffs(diffs)
    assert [r.key for r in result] == ["b", "a"]


# ---------------------------------------------------------------------------
# as_dict / __str__
# ---------------------------------------------------------------------------

def test_as_dict_keys():
    result = deduplicate_diffs([_d("mykey", "v1", "v2")])
    d = result[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "changed", "duplicate_count"}


def test_str_changed_marker():
    r = deduplicate_diffs([_d("k", "a", "b")])[0]
    assert "[~]" in str(r)


def test_str_unchanged_marker():
    r = deduplicate_diffs([_d("k", "a", "a")])[0]
    assert "[=]" in str(r)


def test_str_includes_duplicate_note_when_more_than_one():
    diffs = [_d("k", "a", "a"), _d("k", "b", "b")]
    r = deduplicate_diffs(diffs)[0]
    assert "(x2)" in str(r)


def test_str_no_duplicate_note_when_single():
    r = deduplicate_diffs([_d("k", "a", "a")])[0]
    assert "(x" not in str(r)
