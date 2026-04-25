"""Tests for stackdiff.differ_validator."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_validator import (
    ValidationRule,
    ValidatedDiff,
    validate_diffs,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mixed_diffs() -> list[KeyDiff]:
    return [
        KeyDiff(key="VpcId", baseline_value="vpc-aaa", target_value="vpc-bbb"),
        KeyDiff(key="BucketName", baseline_value="my-bucket", target_value="my-bucket"),
        KeyDiff(key="DbPassword", baseline_value=None, target_value="s3cr3t"),
        KeyDiff(key="OldEndpoint", baseline_value="old.example.com", target_value=None),
    ]


# ---------------------------------------------------------------------------
# Basic structural tests
# ---------------------------------------------------------------------------

def test_returns_validated_diff_instances(mixed_diffs):
    result = validate_diffs(mixed_diffs, rules=[])
    assert all(isinstance(r, ValidatedDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    result = validate_diffs(mixed_diffs, rules=[])
    assert len(result) == len(mixed_diffs)


def test_no_rules_no_violations(mixed_diffs):
    result = validate_diffs(mixed_diffs, rules=[])
    assert all(not r.has_violation for r in result)


# ---------------------------------------------------------------------------
# disallow_changed
# ---------------------------------------------------------------------------

def test_disallow_changed_flags_changed_key(mixed_diffs):
    rules = [ValidationRule(name="no-vpc-change", key_pattern="VpcId", disallow_changed=True)]
    result = validate_diffs(mixed_diffs, rules=rules)
    vpc = next(r for r in result if r.key == "VpcId")
    assert vpc.has_violation


def test_disallow_changed_leaves_unchanged_key(mixed_diffs):
    rules = [ValidationRule(name="no-bucket-change", key_pattern="BucketName", disallow_changed=True)]
    result = validate_diffs(mixed_diffs, rules=rules)
    bucket = next(r for r in result if r.key == "BucketName")
    assert not bucket.has_violation


# ---------------------------------------------------------------------------
# disallow_added
# ---------------------------------------------------------------------------

def test_disallow_added_flags_added_key(mixed_diffs):
    rules = [ValidationRule(name="no-new-secrets", key_pattern="Db*", disallow_added=True)]
    result = validate_diffs(mixed_diffs, rules=rules)
    db = next(r for r in result if r.key == "DbPassword")
    assert db.has_violation


def test_disallow_added_ignores_changed_key(mixed_diffs):
    rules = [ValidationRule(name="no-add-vpc", key_pattern="VpcId", disallow_added=True)]
    result = validate_diffs(mixed_diffs, rules=rules)
    vpc = next(r for r in result if r.key == "VpcId")
    assert not vpc.has_violation


# ---------------------------------------------------------------------------
# disallow_removed
# ---------------------------------------------------------------------------

def test_disallow_removed_flags_removed_key(mixed_diffs):
    rules = [ValidationRule(name="no-remove-endpoint", key_pattern="Old*", disallow_removed=True)]
    result = validate_diffs(mixed_diffs, rules=rules)
    ep = next(r for r in result if r.key == "OldEndpoint")
    assert ep.has_violation


# ---------------------------------------------------------------------------
# Glob patterns
# ---------------------------------------------------------------------------

def test_glob_wildcard_matches_multiple_keys():
    diffs = [
        KeyDiff(key="DbHost", baseline_value="a", target_value="b"),
        KeyDiff(key="DbPort", baseline_value="5432", target_value="5433"),
    ]
    rules = [ValidationRule(name="no-db-change", key_pattern="Db*", disallow_changed=True)]
    result = validate_diffs(diffs, rules=rules)
    assert all(r.has_violation for r in result)


# ---------------------------------------------------------------------------
# Custom message
# ---------------------------------------------------------------------------

def test_custom_message_appears_in_violation(mixed_diffs):
    rules = [
        ValidationRule(
            name="r",
            key_pattern="VpcId",
            disallow_changed=True,
            message="VPC must not change between environments",
        )
    ]
    result = validate_diffs(mixed_diffs, rules=rules)
    vpc = next(r for r in result if r.key == "VpcId")
    assert "VPC must not change" in vpc.violations[0]


# ---------------------------------------------------------------------------
# as_dict
# ---------------------------------------------------------------------------

def test_as_dict_keys(mixed_diffs):
    result = validate_diffs(mixed_diffs, rules=[])
    d = result[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "changed", "violations"}
