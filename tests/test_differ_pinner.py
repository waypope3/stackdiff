"""Tests for stackdiff.differ_pinner."""
import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_pinner import PinnedDiff, pin_diffs, violations


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="DatabaseUrl", baseline_value="db://old", target_value="db://new"),
        KeyDiff(key="BucketName", baseline_value="my-bucket", target_value="my-bucket"),
        KeyDiff(key="ApiKey", baseline_value="key-a", target_value="key-b"),
        KeyDiff(key="Region", baseline_value="us-east-1", target_value="eu-west-1"),
        KeyDiff(key="LogLevel", baseline_value="INFO", target_value="DEBUG"),
    ]


# ---------------------------------------------------------------------------
# pin_diffs
# ---------------------------------------------------------------------------

def test_returns_pinned_diff_instances(mixed_diffs):
    result = pin_diffs(mixed_diffs, [])
    assert all(isinstance(r, PinnedDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    result = pin_diffs(mixed_diffs, ["DatabaseUrl"])
    assert len(result) == len(mixed_diffs)


def test_no_patterns_no_pinned(mixed_diffs):
    result = pin_diffs(mixed_diffs, [])
    assert not any(r.pinned for r in result)


def test_no_patterns_no_violations(mixed_diffs):
    result = pin_diffs(mixed_diffs, [])
    assert not any(r.violation for r in result)


def test_exact_pattern_pins_key(mixed_diffs):
    result = pin_diffs(mixed_diffs, ["DatabaseUrl"])
    pinned_keys = {r.key for r in result if r.pinned}
    assert pinned_keys == {"DatabaseUrl"}


def test_glob_pattern_pins_multiple(mixed_diffs):
    result = pin_diffs(mixed_diffs, ["*Key"])
    pinned_keys = {r.key for r in result if r.pinned}
    assert pinned_keys == {"ApiKey"}


def test_changed_pinned_key_is_violation(mixed_diffs):
    result = pin_diffs(mixed_diffs, ["DatabaseUrl"])
    db_entry = next(r for r in result if r.key == "DatabaseUrl")
    assert db_entry.violation is True


def test_unchanged_pinned_key_is_not_violation(mixed_diffs):
    result = pin_diffs(mixed_diffs, ["BucketName"])
    bucket_entry = next(r for r in result if r.key == "BucketName")
    assert bucket_entry.pinned is True
    assert bucket_entry.violation is False


def test_unpinned_changed_key_not_violation(mixed_diffs):
    result = pin_diffs(mixed_diffs, ["BucketName"])
    region_entry = next(r for r in result if r.key == "Region")
    assert region_entry.pinned is False
    assert region_entry.violation is False


def test_multiple_patterns(mixed_diffs):
    result = pin_diffs(mixed_diffs, ["DatabaseUrl", "Region"])
    pinned_keys = {r.key for r in result if r.pinned}
    assert pinned_keys == {"DatabaseUrl", "Region"}


def test_as_dict_keys(mixed_diffs):
    result = pin_diffs(mixed_diffs, ["DatabaseUrl"])
    d = result[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "changed", "pinned", "violation"}


# ---------------------------------------------------------------------------
# violations helper
# ---------------------------------------------------------------------------

def test_violations_returns_only_violations(mixed_diffs):
    pinned = pin_diffs(mixed_diffs, ["DatabaseUrl", "BucketName", "ApiKey"])
    v = violations(pinned)
    violation_keys = {d.key for d in v}
    # DatabaseUrl changed, BucketName unchanged, ApiKey changed
    assert violation_keys == {"DatabaseUrl", "ApiKey"}


def test_violations_empty_when_none(mixed_diffs):
    pinned = pin_diffs(mixed_diffs, ["BucketName"])
    assert violations(pinned) == []


def test_violations_empty_on_no_patterns(mixed_diffs):
    pinned = pin_diffs(mixed_diffs, [])
    assert violations(pinned) == []
