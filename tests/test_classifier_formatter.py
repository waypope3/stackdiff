"""Tests for classifier_formatter."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_classifier import classify_diffs
from stackdiff.classifier_formatter import format_classified, format_classified_table


@pytest.fixture
def classified():
    diffs = [
        KeyDiff(key="VpcId", baseline="vpc-1", current="vpc-2", changed=True),
        KeyDiff(key="BucketName", baseline="b", current="b", changed=False),
        KeyDiff(key="AppTag", baseline="v1", current="v2", changed=True),
    ]
    return classify_diffs(diffs)


def test_format_classified_contains_category(classified):
    out = format_classified(classified, colour=False)
    assert "NETWORK" in out
    assert "STORAGE" in out


def test_format_classified_shows_key(classified):
    out = format_classified(classified, colour=False)
    assert "VpcId" in out
    assert "BucketName" in out


def test_format_classified_changed_marker(classified):
    out = format_classified(classified, colour=False)
    lines = out.splitlines()
    changed_lines = [l for l in lines if "VpcId" in l]
    assert changed_lines
    assert changed_lines[0].strip().startswith("~")


def test_format_classified_unchanged_marker(classified):
    out = format_classified(classified, colour=False)
    lines = out.splitlines()
    unchanged_lines = [l for l in lines if "BucketName" in l]
    assert unchanged_lines
    assert not unchanged_lines[0].strip().startswith("~")


def test_format_classified_table_header(classified):
    out = format_classified_table(classified)
    assert "KEY" in out
    assert "CATEGORY" in out
    assert "CHANGED" in out


def test_format_classified_table_rows(classified):
    out = format_classified_table(classified)
    assert "VpcId" in out
    assert "network" in out
    assert "yes" in out
