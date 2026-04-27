"""Tests for stackdiff.correlator_formatter."""
from __future__ import annotations

import pytest
from stackdiff.differ_correlator import CorrelatedDiff
from stackdiff.correlator_formatter import (
    format_correlated,
    format_correlated_table,
)


@pytest.fixture()
def diffs():
    return [
        CorrelatedDiff(
            key="VpcId",
            baseline_value="vpc-aaa",
            target_value="vpc-bbb",
            changed=True,
            co_changed_with=["SubnetId", "RouteTableId"],
            correlation_score=0.8750,
        ),
        CorrelatedDiff(
            key="SubnetId",
            baseline_value="subnet-1",
            target_value="subnet-2",
            changed=True,
            co_changed_with=["VpcId"],
            correlation_score=0.8750,
        ),
        CorrelatedDiff(
            key="Region",
            baseline_value="us-east-1",
            target_value="us-east-1",
            changed=False,
            co_changed_with=[],
            correlation_score=0.0,
        ),
    ]


def test_format_correlated_contains_changed_key(diffs):
    out = format_correlated(diffs)
    assert "VpcId" in out


def test_format_correlated_shows_co_changed(diffs):
    out = format_correlated(diffs)
    assert "SubnetId" in out


def test_format_correlated_hides_unchanged_by_default(diffs):
    out = format_correlated(diffs)
    # Region is unchanged; it should not appear unless show_unchanged=True
    assert "Region" not in out


def test_format_correlated_shows_unchanged_when_requested(diffs):
    out = format_correlated(diffs, show_unchanged=True)
    assert "Region" in out


def test_format_correlated_shows_score(diffs):
    out = format_correlated(diffs)
    assert "0.88" in out or "0.87" in out or "0.875" in out


def test_format_correlated_table_contains_header(diffs):
    out = format_correlated_table(diffs)
    assert "KEY" in out
    assert "SCORE" in out


def test_format_correlated_table_shows_changed_key(diffs):
    out = format_correlated_table(diffs)
    assert "VpcId" in out


def test_format_correlated_table_excludes_unchanged(diffs):
    out = format_correlated_table(diffs)
    assert "Region" not in out


def test_format_correlated_table_empty():
    unchanged = [
        CorrelatedDiff(
            key="A", baseline_value="x", target_value="x",
            changed=False, co_changed_with=[], correlation_score=0.0,
        )
    ]
    out = format_correlated_table(unchanged)
    assert "no changed keys" in out
