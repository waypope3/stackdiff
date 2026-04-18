"""Tests for stackdiff.annotator."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.annotator import annotate_diffs, AnnotatedDiff


def _diff(key, baseline, target):
    return KeyDiff(key=key, baseline=baseline, target=target)


def test_changed_status():
    result = annotate_diffs([_diff("Env", "prod", "staging")])
    assert result[0].status == "changed"


def test_added_status():
    result = annotate_diffs([_diff("NewKey", None, "hello")])
    assert result[0].status == "added"


def test_removed_status():
    result = annotate_diffs([_diff("OldKey", "bye", None)])
    assert result[0].status == "removed"


def test_unchanged_status():
    result = annotate_diffs([_diff("Same", "x", "x")])
    assert result[0].status == "unchanged"


def test_changed_annotation_contains_values():
    result = annotate_diffs([_diff("Env", "prod", "staging")])
    ann = result[0].annotation
    assert "prod" in ann
    assert "staging" in ann
    assert "Env" in ann


def test_added_annotation_mentions_new():
    result = annotate_diffs([_diff("K", None, "v")])
    assert "new" in result[0].annotation.lower()


def test_removed_annotation_mentions_removed():
    result = annotate_diffs([_diff("K", "v", None)])
    assert "removed" in result[0].annotation.lower()


def test_unchanged_annotation_mentions_unchanged():
    result = annotate_diffs([_diff("K", "v", "v")])
    assert "unchanged" in result[0].annotation.lower()


def test_returns_annotated_diff_instances():
    result = annotate_diffs([_diff("A", "1", "2")])
    assert isinstance(result[0], AnnotatedDiff)


def test_empty_input():
    assert annotate_diffs([]) == []


def test_multiple_diffs_length():
    diffs = [_diff("A", "1", "2"), _diff("B", None, "3"), _diff("C", "x", "x")]
    result = annotate_diffs(diffs)
    assert len(result) == 3


def test_key_preserved():
    result = annotate_diffs([_diff("MyKey", "a", "b")])
    assert result[0].key == "MyKey"
