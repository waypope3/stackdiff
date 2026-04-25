"""Tests for stackdiff.indexer_formatter."""
import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_indexer import index_diffs
from stackdiff.indexer_formatter import (
    format_index,
    format_index_entry,
    format_index_table,
)


@pytest.fixture()
def index():
    diffs = [
        KeyDiff(key="VpcId", baseline_value="vpc-old", target_value="vpc-new"),
        KeyDiff(key="SubnetId", baseline_value="sub-1", target_value="sub-1"),
        KeyDiff(key="NewKey", baseline_value=None, target_value="val"),
        KeyDiff(key="GoneKey", baseline_value="old", target_value=None),
    ]
    return index_diffs(diffs)


def test_format_index_contains_total(index):
    out = format_index(index, colour=False)
    assert "total=4" in out


def test_format_index_shows_changed_key(index):
    out = format_index(index, colour=False)
    assert "VpcId" in out


def test_format_index_shows_added_marker(index):
    out = format_index(index, colour=False)
    assert "+" in out


def test_format_index_shows_removed_marker(index):
    out = format_index(index, colour=False)
    assert "-" in out


def test_format_index_filter_by_status(index):
    out = format_index(index, statuses=["added"], colour=False)
    assert "NewKey" in out
    assert "VpcId" not in out


def test_format_index_empty_filter_returns_no_entries(index):
    out = format_index(index, statuses=["nonexistent"], colour=False)
    assert "no entries" in out


def test_format_index_entry_changed(index):
    entry = index.lookup("VpcId")
    out = format_index_entry(entry, colour=False)
    assert "VpcId" in out
    assert "vpc-old" in out
    assert "vpc-new" in out


def test_format_index_entry_added(index):
    entry = index.lookup("NewKey")
    out = format_index_entry(entry, colour=False)
    assert "+" in out
    assert "val" in out


def test_format_index_entry_removed(index):
    entry = index.lookup("GoneKey")
    out = format_index_entry(entry, colour=False)
    assert "-" in out
    assert "old" in out


def test_format_index_table_contains_status_labels(index):
    out = format_index_table(index, colour=False)
    for status in ("Changed", "Added", "Removed", "Unchanged"):
        assert status in out


def test_format_index_table_correct_counts(index):
    out = format_index_table(index, colour=False)
    # 1 changed, 1 added, 1 removed, 1 unchanged
    lines = out.splitlines()
    data_lines = [l for l in lines if l.strip() and not l.startswith("-") and not l.startswith("Status")]
    counts = [int(l.split()[-1]) for l in data_lines]
    assert counts == [1, 1, 1, 1]
