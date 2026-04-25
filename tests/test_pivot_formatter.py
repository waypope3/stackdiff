"""Tests for stackdiff.pivot_formatter."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_pivot import pivot_diffs
from stackdiff.pivot_formatter import format_pivot, format_pivot_table


@pytest.fixture()
def _diffs() -> list[KeyDiff]:
    return [
        KeyDiff(key="VpcId", baseline_value="old", target_value="new"),
        KeyDiff(key="SubnetId", baseline_value=None, target_value="subnet-1"),
        KeyDiff(key="Region", baseline_value="us-east-1", target_value="us-east-1"),
    ]


def test_format_pivot_contains_dimension(_diffs):
    result = pivot_diffs(_diffs, "status")
    out = format_pivot(result, colour=False)
    assert "status" in out


def test_format_pivot_shows_changed(_diffs):
    result = pivot_diffs(_diffs, "status")
    out = format_pivot(result, colour=False)
    assert "changed" in out


def test_format_pivot_shows_added(_diffs):
    result = pivot_diffs(_diffs, "status")
    out = format_pivot(result, colour=False)
    assert "added" in out


def test_format_pivot_shows_total(_diffs):
    result = pivot_diffs(_diffs, "status")
    out = format_pivot(result, colour=False)
    assert "total" in out
    assert "3" in out


def test_format_pivot_colour_does_not_crash(_diffs):
    result = pivot_diffs(_diffs, "status")
    out = format_pivot(result, colour=True)
    assert "status" in out


def test_format_pivot_table_contains_dimension(_diffs):
    result = pivot_diffs(_diffs, "status")
    out = format_pivot_table(result, colour=False)
    assert "status" in out


def test_format_pivot_table_lists_key(_diffs):
    result = pivot_diffs(_diffs, "status")
    out = format_pivot_table(result, colour=False)
    assert "VpcId" in out


def test_format_pivot_table_shows_added_key(_diffs):
    result = pivot_diffs(_diffs, "status")
    out = format_pivot_table(result, colour=False)
    assert "SubnetId" in out


def test_format_pivot_table_colour_does_not_crash(_diffs):
    result = pivot_diffs(_diffs, "status")
    out = format_pivot_table(result, colour=True)
    assert "VpcId" in out


def test_format_pivot_empty():
    result = pivot_diffs([], "status")
    out = format_pivot(result, colour=False)
    assert "total" in out
    assert "0" in out
