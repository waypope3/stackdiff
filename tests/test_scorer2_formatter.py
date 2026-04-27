"""Tests for scorer2_formatter."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_scorer2 import score_diffs_extended
from stackdiff.scorer2_formatter import format_extended_score, format_extended_score_table


@pytest.fixture()
def score():
    diffs = [
        KeyDiff(key="VpcId", baseline="vpc-old", target="vpc-new"),
        KeyDiff(key="DbEndpoint", baseline="db.host", target="db.host"),
        KeyDiff(key="RoleArn", baseline="arn:old", target="arn:new"),
        KeyDiff(key="PlainKey", baseline="same", target="same"),
    ]
    return score_diffs_extended(diffs)


def test_format_score_contains_header(score):
    output = format_extended_score(score)
    assert "Extended Diff Score" in output


def test_format_score_shows_changed_key(score):
    output = format_extended_score(score)
    assert "VpcId" in output


def test_format_score_hides_unchanged_by_default(score):
    output = format_extended_score(score)
    assert "DbEndpoint" not in output


def test_format_score_shows_unchanged_when_requested(score):
    output = format_extended_score(score, show_unchanged=True)
    assert "DbEndpoint" in output


def test_format_score_contains_domain(score):
    output = format_extended_score(score)
    assert "network" in output or "iam" in output


def test_format_score_contains_severity(score):
    output = format_extended_score(score)
    assert any(s in output for s in ("HIGH", "MEDIUM", "LOW"))


def test_format_score_table_contains_header(score):
    output = format_extended_score_table(score)
    assert "KEY" in output
    assert "DOMAIN" in output
    assert "WEIGHT" in output


def test_format_score_table_contains_all_keys(score):
    output = format_extended_score_table(score)
    for key in ("VpcId", "DbEndpoint", "RoleArn", "PlainKey"):
        assert key in output


def test_format_score_table_contains_total_row(score):
    output = format_extended_score_table(score)
    assert "TOTAL" in output


def test_format_score_empty():
    from stackdiff.differ_scorer2 import ExtendedScore
    empty = ExtendedScore()
    out = format_extended_score(empty)
    assert "Extended Diff Score" in out
    out_table = format_extended_score_table(empty)
    assert "TOTAL" in out_table
