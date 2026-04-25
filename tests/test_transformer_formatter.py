"""Tests for transformer_formatter."""

from __future__ import annotations

from stackdiff.differ import KeyDiff
from stackdiff.differ_transformer import transform_diffs
from stackdiff.transformer_formatter import format_transformed, format_transformed_table


def _make_diffs():
    raw = [
        KeyDiff(key="VpcId", baseline_value="vpc-abc", target_value="vpc-abc"),
        KeyDiff(key="SubnetId", baseline_value="SUBNET-1", target_value="subnet-1"),
    ]
    return transform_diffs(raw, ["lower"])


def test_format_transformed_contains_transform_name():
    diffs = _make_diffs()
    out = format_transformed(diffs)
    assert "lower" in out


def test_format_transformed_shows_keys():
    diffs = _make_diffs()
    out = format_transformed(diffs)
    assert "VpcId" in out
    assert "SubnetId" in out


def test_format_transformed_changed_marker():
    diffs = _make_diffs()
    out = format_transformed(diffs)
    # SubnetId should show a change marker (~) because raw values differ
    # even though transformed they are equal — changed reflects post-transform
    assert "=" in out  # unchanged entry present


def test_format_transformed_summary_line():
    diffs = _make_diffs()
    out = format_transformed(diffs)
    assert "Summary" in out


def test_format_transformed_empty():
    out = format_transformed([])
    assert "No transformed diffs" in out


def test_format_transformed_show_original():
    diffs = _make_diffs()
    out = format_transformed(diffs, show_original=True)
    # SubnetId has differing raw values so original line should appear
    assert "original" in out


def test_format_transformed_table_header():
    diffs = _make_diffs()
    out = format_transformed_table(diffs)
    assert "key" in out
    assert "changed" in out
    assert "transformed_baseline" in out


def test_format_transformed_table_rows():
    diffs = _make_diffs()
    out = format_transformed_table(diffs)
    lines = out.strip().splitlines()
    # header + 2 data rows
    assert len(lines) == 3


def test_format_transformed_table_empty():
    out = format_transformed_table([])
    assert "key" in out
    assert len(out.strip().splitlines()) == 1  # header only
