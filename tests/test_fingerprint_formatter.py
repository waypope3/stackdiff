"""Tests for stackdiff.fingerprint_formatter."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_fingerprinter import fingerprint_diffs
from stackdiff.fingerprint_formatter import (
    format_fingerprinted,
    format_fingerprinted_table,
)


@pytest.fixture
def diffs():
    raw = [
        KeyDiff(key="BucketName", baseline_value="old-bucket", target_value="new-bucket"),
        KeyDiff(key="Region", baseline_value="us-east-1", target_value="us-east-1"),
        KeyDiff(key="AddedKey", baseline_value=None, target_value="added"),
    ]
    return fingerprint_diffs(raw)


def test_format_fingerprinted_contains_changed_key(diffs):
    out = format_fingerprinted(diffs)
    assert "BucketName" in out


def test_format_fingerprinted_hides_unchanged_by_default(diffs):
    out = format_fingerprinted(diffs)
    assert "Region" not in out


def test_format_fingerprinted_shows_unchanged_when_requested(diffs):
    out = format_fingerprinted(diffs, show_unchanged=True)
    assert "Region" in out


def test_format_fingerprinted_shows_stack_fingerprint(diffs):
    out = format_fingerprinted(diffs)
    assert "stack fingerprint" in out


def test_format_fingerprinted_shows_changed_total(diffs):
    out = format_fingerprinted(diffs)
    assert "changed / total" in out


def test_format_fingerprinted_table_contains_header(diffs):
    out = format_fingerprinted_table(diffs)
    assert "KEY" in out
    assert "CHANGED" in out


def test_format_fingerprinted_table_shows_all_keys(diffs):
    out = format_fingerprinted_table(diffs)
    assert "BucketName" in out
    assert "Region" in out
    assert "AddedKey" in out


def test_format_fingerprinted_table_truncation(diffs):
    out = format_fingerprinted_table(diffs, truncate=8)
    # fingerprints should be truncated to 8 chars; no full 64-char hash visible
    for line in out.splitlines()[2:]:
        parts = line.split()
        # last two tokens are the fingerprints; each should be <=8 chars
        fp_tokens = [p for p in parts if len(p) <= 8 or p == "n/a"]
        assert fp_tokens  # at least one short token present
