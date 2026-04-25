"""Tests for stackdiff.mapper_formatter."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_mapper import map_diffs
from stackdiff.mapper_formatter import format_mapped, format_mapped_table


@pytest.fixture()
def diffs():
    raw = [
        KeyDiff(key="VpcId", baseline_value="vpc-111", target_value="vpc-222"),
        KeyDiff(key="SubnetId", baseline_value="subnet-aaa", target_value="subnet-aaa"),
        KeyDiff(key="DbEndpoint", baseline_value=None, target_value="db.host"),
    ]
    return map_diffs(raw, mapping={"VpcId": "Virtual Network"})


def test_format_mapped_contains_mapped_key(diffs):
    output = format_mapped(diffs, colour=False)
    assert "Virtual Network" in output


def test_format_mapped_shows_remap_note(diffs):
    output = format_mapped(diffs, colour=False)
    assert "VpcId" in output  # original key shown in remap note


def test_format_mapped_changed_marker(diffs):
    output = format_mapped(diffs, colour=False)
    assert "[~]" in output or "[+]" in output


def test_format_mapped_unchanged_marker(diffs):
    output = format_mapped(diffs, colour=False)
    assert "[ ]" in output


def test_format_mapped_added_marker(diffs):
    output = format_mapped(diffs, colour=False)
    assert "[+]" in output


def test_format_mapped_table_has_header(diffs):
    table = format_mapped_table(diffs)
    assert "KEY" in table
    assert "ORIGINAL" in table
    assert "BASELINE" in table
    assert "TARGET" in table


def test_format_mapped_table_row_count(diffs):
    table = format_mapped_table(diffs)
    # header + separator + 3 data rows
    lines = table.strip().splitlines()
    assert len(lines) == 5


def test_format_mapped_table_contains_mapped_key(diffs):
    table = format_mapped_table(diffs)
    assert "Virtual Network" in table
