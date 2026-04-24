"""Tests for differ_highlighter and highlight_formatter."""
import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_highlighter import highlight_diffs, HighlightedDiff
from stackdiff.highlight_formatter import format_highlighted, format_highlighted_table


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="Endpoint", baseline_value="http://old.example.com", target_value="http://new.example.com"),
        KeyDiff(key="Region", baseline_value="us-east-1", target_value="us-east-1"),
        KeyDiff(key="BucketName", baseline_value=None, target_value="my-bucket"),
        KeyDiff(key="OldKey", baseline_value="gone", target_value=None),
    ]


# ---------------------------------------------------------------------------
# highlight_diffs
# ---------------------------------------------------------------------------

def test_returns_highlighted_diff_instances(mixed_diffs):
    result = highlight_diffs(mixed_diffs)
    assert all(isinstance(r, HighlightedDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    result = highlight_diffs(mixed_diffs)
    assert len(result) == len(mixed_diffs)


def test_changed_flag_set_for_different_values(mixed_diffs):
    result = highlight_diffs(mixed_diffs)
    assert result[0].changed is True   # Endpoint changed
    assert result[1].changed is False  # Region unchanged


def test_added_key_marked_changed(mixed_diffs):
    result = highlight_diffs(mixed_diffs)
    added = next(r for r in result if r.key == "BucketName")
    assert added.changed is True
    assert added.baseline_highlighted == ""


def test_removed_key_marked_changed(mixed_diffs):
    result = highlight_diffs(mixed_diffs)
    removed = next(r for r in result if r.key == "OldKey")
    assert removed.changed is True
    assert removed.target_highlighted == ""


def test_no_colour_returns_plain_strings():
    diffs = [KeyDiff(key="k", baseline_value="aaa", target_value="bbb")]
    result = highlight_diffs(diffs, colour=False)
    assert result[0].baseline_highlighted == "aaa"
    assert result[0].target_highlighted == "bbb"


def test_opcodes_populated_when_changed():
    diffs = [KeyDiff(key="k", baseline_value="hello", target_value="helo")]
    result = highlight_diffs(diffs, colour=True)
    assert len(result[0].opcodes) > 0


def test_as_dict_contains_expected_keys(mixed_diffs):
    result = highlight_diffs(mixed_diffs, colour=False)
    d = result[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_highlighted", "target_highlighted", "changed"}


# ---------------------------------------------------------------------------
# format_highlighted
# ---------------------------------------------------------------------------

def test_format_highlighted_skips_unchanged_by_default(mixed_diffs):
    highlighted = highlight_diffs(mixed_diffs, colour=False)
    output = format_highlighted(highlighted, colour=False)
    assert "Region" not in output


def test_format_highlighted_shows_unchanged_when_requested(mixed_diffs):
    highlighted = highlight_diffs(mixed_diffs, colour=False)
    output = format_highlighted(highlighted, colour=False, show_unchanged=True)
    assert "Region" in output


def test_format_highlighted_contains_changed_key(mixed_diffs):
    highlighted = highlight_diffs(mixed_diffs, colour=False)
    output = format_highlighted(highlighted, colour=False)
    assert "Endpoint" in output


# ---------------------------------------------------------------------------
# format_highlighted_table
# ---------------------------------------------------------------------------

def test_format_table_no_diffs_returns_message():
    diffs = [KeyDiff(key="k", baseline_value="x", target_value="x")]
    highlighted = highlight_diffs(diffs, colour=False)
    output = format_highlighted_table(highlighted, colour=False, show_unchanged=False)
    assert output == "(no differences)"


def test_format_table_contains_header(mixed_diffs):
    highlighted = highlight_diffs(mixed_diffs, colour=False)
    output = format_highlighted_table(highlighted, colour=False)
    assert "KEY" in output
    assert "BASELINE" in output
    assert "TARGET" in output


def test_format_table_lists_changed_key(mixed_diffs):
    highlighted = highlight_diffs(mixed_diffs, colour=False)
    output = format_highlighted_table(highlighted, colour=False)
    assert "Endpoint" in output
