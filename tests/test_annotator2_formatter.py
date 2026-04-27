"""Tests for stackdiff.annotator2_formatter."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_annotator import annotate_diffs2
from stackdiff.annotator2_formatter import format_annotated2, format_annotated2_table


@pytest.fixture()
def diffs():
    raw = [
        KeyDiff(key="VpcId", baseline_value="vpc-aaa", target_value="vpc-bbb"),
        KeyDiff(key="BucketArn", baseline_value=None, target_value="arn:aws:s3:::new"),
        KeyDiff(key="OldKey", baseline_value="x", target_value=None),
        KeyDiff(key="StableKey", baseline_value="same", target_value="same"),
    ]
    return annotate_diffs2(raw)


def test_format_annotated2_contains_changed_key(diffs):
    out = format_annotated2(diffs)
    assert "VpcId" in out


def test_format_annotated2_hides_unchanged_by_default(diffs):
    out = format_annotated2(diffs)
    assert "StableKey" not in out


def test_format_annotated2_shows_unchanged_when_requested(diffs):
    out = format_annotated2(diffs, show_unchanged=True)
    assert "StableKey" in out


def test_format_annotated2_shows_domain_tag(diffs):
    out = format_annotated2(diffs)
    assert "network" in out


def test_format_annotated2_shows_arn_hint(diffs):
    out = format_annotated2(diffs)
    assert "arn" in out


def test_format_annotated2_summary_line(diffs):
    out = format_annotated2(diffs)
    assert "keys changed" in out


def test_format_annotated2_table_contains_header(diffs):
    out = format_annotated2_table(diffs)
    assert "KEY" in out
    assert "DOMAIN" in out
    assert "STATUS" in out


def test_format_annotated2_table_shows_added_status(diffs):
    out = format_annotated2_table(diffs)
    assert "added" in out


def test_format_annotated2_table_shows_removed_status(diffs):
    out = format_annotated2_table(diffs)
    assert "removed" in out


def test_format_annotated2_table_shows_all_keys(diffs):
    out = format_annotated2_table(diffs)
    for key in ["VpcId", "BucketArn", "OldKey", "StableKey"]:
        assert key in out
