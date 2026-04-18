"""Tests for stackdiff.truncator."""

import pytest

from stackdiff.truncator import DEFAULT_MAX_LENGTH, truncate_diff, truncate_value


# ---------------------------------------------------------------------------
# truncate_value
# ---------------------------------------------------------------------------

def test_short_string_unchanged():
    assert truncate_value("hello") == "hello"


def test_exact_max_length_unchanged():
    s = "x" * DEFAULT_MAX_LENGTH
    assert truncate_value(s) == s


def test_long_string_truncated():
    s = "a" * 200
    result = truncate_value(s, max_length=10)
    assert len(result) == 10
    assert result.endswith("...")


def test_custom_max_length():
    result = truncate_value("abcdefgh", max_length=5)
    assert result == "ab..."
    assert len(result) == 5


def test_non_string_raises():
    with pytest.raises(TypeError):
        truncate_value(123)  # type: ignore[arg-type]


def test_max_length_too_small_raises():
    with pytest.raises(ValueError):
        truncate_value("hello", max_length=2)


def test_empty_string_unchanged():
    assert truncate_value("") == ""


def test_truncated_prefix_contains_original_content():
    """Ensure the kept prefix is actually from the original string."""
    s = "abcdefghij"
    result = truncate_value(s, max_length=6)
    # First 3 chars should be the original content, last 3 are ellipsis
    assert result == "abc..."


# ---------------------------------------------------------------------------
# truncate_diff
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_diff():
    return {
        "KeyA": {"baseline": "short", "target": "also short", "status": "changed"},
        "KeyB": {"baseline": "x" * 200, "target": "y" * 200, "status": "changed"},
        "KeyC": {"baseline": None, "target": "new-value", "status": "added"},
    }


def test_short_values_unchanged(sample_diff):
    result = truncate_diff(sample_diff, max_length=50)
    assert result["KeyA"]["baseline"] == "short"
    assert result["KeyA"]["target"] == "also short"


def test_long_values_truncated(sample_diff):
    result = truncate_diff(sample_diff, max_length=50)
    assert len(result["KeyB"]["baseline"]) == 50
    assert result["KeyB"]["baseline"].endswith("...")
    assert len(result["KeyB"]["target"]) == 50


def test_none_value_preserved(sample_diff):
    result = truncate_diff(sample_diff, max_length=50)
    assert result["KeyC"]["baseline"] is None


def test_extra_fields_preserved(sample_diff):
    result = truncate_diff(sample_diff, max_length=50)
    assert result["KeyA"]["status"] == "changed"


def test_original_diff_not_mutated(sample_diff):
    original_val = sample_diff["KeyB"]["baseline"]
    truncate_diff(sample_diff, max_length=50)
    assert sample_diff["KeyB"]["baseline"] == original_val


def test_truncate_diff_returns_new_dict(sample_diff):
    """truncate_diff should return a new dict, not the original."""
    result = truncate_diff(sample_diff, max_length=50)
    assert result is not sample_diff
    assert result["KeyA"] is not sample_diff["KeyA"]
