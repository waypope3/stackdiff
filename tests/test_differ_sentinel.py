"""Tests for stackdiff.differ_sentinel."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_sentinel import (
    SentinelRule,
    SentinelledDiff,
    sentinel_diffs,
)


@pytest.fixture()
def mixed_diffs() -> list[KeyDiff]:
    return [
        KeyDiff(key="VpcId", old_value="vpc-aaa", new_value="vpc-bbb"),
        KeyDiff(key="DbPassword", old_value="secret", new_value="newsecret"),
        KeyDiff(key="BucketName", old_value="my-bucket", new_value="my-bucket"),
        KeyDiff(key="SubnetId", old_value=None, new_value="subnet-123"),
        KeyDiff(key="OldParam", old_value="x", new_value=None),
    ]


def test_returns_sentinelled_diff_instances(mixed_diffs):
    result = sentinel_diffs(mixed_diffs, rules=[])
    assert all(isinstance(r, SentinelledDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    result = sentinel_diffs(mixed_diffs, rules=[])
    assert len(result) == len(mixed_diffs)


def test_no_rules_no_alerts(mixed_diffs):
    result = sentinel_diffs(mixed_diffs, rules=[])
    assert not any(r.alerted for r in result)


def test_no_rules_changed_flag_correct(mixed_diffs):
    result = sentinel_diffs(mixed_diffs, rules=[])
    by_key = {r.key: r for r in result}
    assert by_key["VpcId"].changed is True
    assert by_key["BucketName"].changed is False


def test_exact_pattern_triggers_alert(mixed_diffs):
    rules = [SentinelRule(pattern="DbPassword", message="password changed")]
    result = sentinel_diffs(mixed_diffs, rules=rules)
    by_key = {r.key: r for r in result}
    assert by_key["DbPassword"].alerted is True
    assert by_key["DbPassword"].alert_message == "password changed"


def test_glob_pattern_triggers_alert(mixed_diffs):
    rules = [SentinelRule(pattern="Vpc*", message="vpc change")]
    result = sentinel_diffs(mixed_diffs, rules=rules)
    by_key = {r.key: r for r in result}
    assert by_key["VpcId"].alerted is True
    assert by_key["BucketName"].alerted is False


def test_change_type_added_triggers_rule(mixed_diffs):
    rules = [SentinelRule(pattern="SubnetId", change_types=["added"])]
    result = sentinel_diffs(mixed_diffs, rules=rules)
    by_key = {r.key: r for r in result}
    assert by_key["SubnetId"].alerted is True


def test_change_type_removed_triggers_rule(mixed_diffs):
    rules = [SentinelRule(pattern="OldParam", change_types=["removed"])]
    result = sentinel_diffs(mixed_diffs, rules=rules)
    by_key = {r.key: r for r in result}
    assert by_key["OldParam"].alerted is True


def test_change_type_mismatch_no_alert(mixed_diffs):
    # VpcId is 'changed', not 'added'
    rules = [SentinelRule(pattern="VpcId", change_types=["added"])]
    result = sentinel_diffs(mixed_diffs, rules=rules)
    by_key = {r.key: r for r in result}
    assert by_key["VpcId"].alerted is False


def test_unchanged_key_not_alerted_by_changed_rule(mixed_diffs):
    rules = [SentinelRule(pattern="BucketName", change_types=["changed"])]
    result = sentinel_diffs(mixed_diffs, rules=rules)
    by_key = {r.key: r for r in result}
    assert by_key["BucketName"].alerted is False


def test_matched_rule_pattern_stored(mixed_diffs):
    rules = [SentinelRule(pattern="Db*", message="db alert")]
    result = sentinel_diffs(mixed_diffs, rules=rules)
    by_key = {r.key: r for r in result}
    assert by_key["DbPassword"].matched_rule == "Db*"


def test_as_dict_keys(mixed_diffs):
    result = sentinel_diffs(mixed_diffs, rules=[])
    d = result[0].as_dict()
    assert {"key", "old_value", "new_value", "changed", "alerted", "alert_message", "matched_rule"} == set(d.keys())


def test_str_alerted(mixed_diffs):
    rules = [SentinelRule(pattern="VpcId", message="vpc")]
    result = sentinel_diffs(mixed_diffs, rules=rules)
    by_key = {r.key: r for r in result}
    assert "[ALERT]" in str(by_key["VpcId"])


def test_str_not_alerted(mixed_diffs):
    result = sentinel_diffs(mixed_diffs, rules=[])
    by_key = {r.key: r for r in result}
    assert "[ok]" in str(by_key["BucketName"])
