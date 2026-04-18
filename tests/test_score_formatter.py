"""Tests for stackdiff.score_formatter."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_scorer import score_diffs
from stackdiff.score_formatter import format_score, format_score_table


def _d(status: str) -> KeyDiff:
    return KeyDiff(key="k", baseline="a", target="b", status=status)


@pytest.fixture()
def high_score():
    return score_diffs([_d("changed")] * 3 + [_d("unchanged")])


@pytest.fixture()
def none_score():
    return score_diffs([_d("unchanged")] * 4)


def test_format_score_contains_severity(high_score):
    out = format_score(high_score, colour=False)
    assert "MEDIUM" in out or "HIGH" in out


def test_format_score_contains_pct(high_score):
    out = format_score(high_score, colour=False)
    assert "%" in out


def test_format_score_none_severity(none_score):
    out = format_score(none_score, colour=False)
    assert "NONE" in out


def test_format_score_no_colour_no_escape(high_score):
    out = format_score(high_score, colour=False)
    assert "\033[" not in out


def test_format_score_colour_has_escape(high_score):
    out = format_score(high_score, colour=True)
    assert "\033[" in out


def test_format_score_table_multiline(high_score):
    out = format_score_table(high_score, colour=False)
    assert len(out.splitlines()) >= 5


def test_format_score_table_contains_total(high_score):
    out = format_score_table(high_score, colour=False)
    assert "Total keys" in out


def test_format_score_table_no_colour_no_escape(none_score):
    out = format_score_table(none_score, colour=False)
    assert "\033[" not in out
