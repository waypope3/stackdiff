"""Tests for stackdiff.differ_normalizer."""
import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_normalizer import (
    NormalizedDiff,
    normalize_diffs,
    _normalise_value,
    _normalise_key,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _diff(key: str, baseline, target) -> KeyDiff:
    return KeyDiff(key=key, baseline=baseline, target=target)


# ---------------------------------------------------------------------------
# _normalise_value
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("hello", "hello"),
    ("  spaced  ", "spaced"),
    (None, ""),
    ("True", "true"),
    ("YES", "true"),
    ("1", "true"),
    ("on", "true"),
    ("False", "false"),
    ("NO", "false"),
    ("0", "false"),
    ("off", "false"),
    (42, "42"),
])
def test_normalise_value(raw, expected):
    assert _normalise_value(raw) == expected


# ---------------------------------------------------------------------------
# _normalise_key
# ---------------------------------------------------------------------------

def test_normalise_key_strips_and_lowercases():
    assert _normalise_key("  MyKey  ") == "mykey"


def test_normalise_key_already_clean():
    assert _normalise_key("dburl") == "dburl"


# ---------------------------------------------------------------------------
# normalize_diffs — basic
# ---------------------------------------------------------------------------

def test_returns_normalized_diff_instances():
    result = normalize_diffs([_diff("k", "a", "b")])
    assert len(result) == 1
    assert isinstance(result[0], NormalizedDiff)


def test_changed_when_values_differ():
    (nd,) = normalize_diffs([_diff("k", "old", "new")])
    assert nd.changed is True


def test_unchanged_when_values_equal():
    (nd,) = normalize_diffs([_diff("k", "same", "same")])
    assert nd.changed is False


def test_bool_coercion_treats_true_variants_as_equal():
    (nd,) = normalize_diffs([_diff("flag", "True", "yes")])
    assert nd.changed is False


def test_none_treated_as_empty_string():
    (nd,) = normalize_diffs([_diff("k", None, "")])
    assert nd.changed is False


def test_raw_values_preserved():
    (nd,) = normalize_diffs([_diff("k", "  hi  ", "hi")])
    assert nd.baseline_raw == "  hi  "
    assert nd.target_raw == "hi"


# ---------------------------------------------------------------------------
# normalize_diffs — case_insensitive_keys
# ---------------------------------------------------------------------------

def test_key_unchanged_by_default():
    (nd,) = normalize_diffs([_diff("MyKey", "v", "v")])
    assert nd.key == "MyKey"


def test_key_lowercased_when_flag_set():
    (nd,) = normalize_diffs([_diff("MyKey", "v", "v")], case_insensitive_keys=True)
    assert nd.key == "mykey"


# ---------------------------------------------------------------------------
# as_dict
# ---------------------------------------------------------------------------

def test_as_dict_contains_expected_keys():
    (nd,) = normalize_diffs([_diff("x", "1", "2")])
    d = nd.as_dict()
    assert set(d.keys()) == {"key", "baseline_raw", "target_raw", "baseline_norm", "target_norm", "changed"}


def test_empty_list_returns_empty():
    assert normalize_diffs([]) == []
