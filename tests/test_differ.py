"""Tests for stackdiff.differ and stackdiff.formatter."""

import io
import pytest

from stackdiff.differ import diff_stacks, DiffResult
from stackdiff.formatter import format_diff


BASE = {"region": "us-east-1", "bucket": "my-bucket", "removed_key": "old"}
TARGET = {"region": "us-west-2", "bucket": "my-bucket", "added_key": "new"}


@pytest.fixture
def result() -> DiffResult:
    return diff_stacks(BASE, TARGET)


def test_changed_key(result):
    assert "region" in result.changed
    assert result.changed["region"] == ("us-east-1", "us-west-2")


def test_unchanged_key(result):
    assert "bucket" in result.unchanged
    assert result.unchanged["bucket"] == "my-bucket"


def test_removed_key(result):
    assert "removed_key" in result.removed
    assert result.removed["removed_key"] == "old"


def test_added_key(result):
    assert "added_key" in result.added
    assert result.added["added_key"] == "new"


def test_has_diff(result):
    assert result.has_diff is True


def test_no_diff():
    r = diff_stacks({"a": 1}, {"a": 1})
    assert not r.has_diff
    assert "No differences" in r.summary()


def test_summary_contains_counts(result):
    s = result.summary()
    assert "+1" in s
    assert "-1" in s
    assert "~1" in s


def test_format_diff_plain(result):
    buf = io.StringIO()
    format_diff(result, out=buf, use_colour=False)
    output = buf.getvalue()
    assert "+ added_key = new" in output
    assert "- removed_key = old" in output
    assert "- region = us-east-1" in output
    assert "+ region = us-west-2" in output


def test_format_diff_colour(result):
    buf = io.StringIO()
    format_diff(result, out=buf, use_colour=True)
    output = buf.getvalue()
    assert "\033[32m" in output
    assert "\033[31m" in output
