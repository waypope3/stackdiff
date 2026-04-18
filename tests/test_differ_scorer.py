"""Tests for stackdiff.differ_scorer."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_scorer import score_diffs, DiffScore


def _d(status: str) -> KeyDiff:
    return KeyDiff(key="k", baseline="a", target="b", status=status)


@pytest.fixture()
def mixed_diffs():
    return [
        _d("changed"),
        _d("added"),
        _d("removed"),
        _d("unchanged"),
    ]


def test_counts(mixed_diffs):
    s = score_diffs(mixed_diffs)
    assert s.changed == 1
    assert s.added == 1
    assert s.removed == 1
    assert s.total == 4


def test_score_value(mixed_diffs):
    s = score_diffs(mixed_diffs)
    assert s.score == pytest.approx(0.75)


def test_severity_high(mixed_diffs):
    assert score_diffs(mixed_diffs).severity == "high"


def test_severity_none():
    diffs = [_d("unchanged")] * 4
    s = score_diffs(diffs)
    assert s.severity == "none"
    assert s.score == 0.0


def test_severity_low():
    diffs = [_d("changed")] + [_d("unchanged")] * 9
    assert score_diffs(diffs).severity == "low"


def test_severity_medium():
    diffs = [_d("changed")] * 3 + [_d("unchanged")] * 4
    s = score_diffs(diffs)
    assert s.severity == "medium"


def test_empty_list():
    s = score_diffs([])
    assert s.total == 0
    assert s.score == 0.0
    assert s.severity == "none"


def test_as_dict_keys(mixed_diffs):
    d = score_diffs(mixed_diffs).as_dict()
    assert set(d.keys()) == {"total", "changed", "added", "removed", "score", "severity"}


def test_str_contains_severity(mixed_diffs):
    assert "high" in str(score_diffs(mixed_diffs))
