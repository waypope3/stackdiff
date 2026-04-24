"""Tests for stackdiff.differ_pruner."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_pruner import (
    PruneRule,
    PrunedDiff,
    active_diffs,
    prune_diffs,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mixed_diffs() -> list[KeyDiff]:
    return [
        KeyDiff(key="DatabasePassword", baseline="secret1", target="secret2"),
        KeyDiff(key="BucketName", baseline="my-bucket", target="my-bucket"),
        KeyDiff(key="LastUpdated", baseline="2024-01-01", target="2024-06-15"),
        KeyDiff(key="VpcId", baseline="vpc-abc", target="vpc-xyz"),
    ]


# ---------------------------------------------------------------------------
# prune_diffs – basic behaviour
# ---------------------------------------------------------------------------

def test_returns_pruned_diff_instances(mixed_diffs):
    result = prune_diffs(mixed_diffs, rules=[])
    assert all(isinstance(r, PrunedDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    result = prune_diffs(mixed_diffs, rules=[])
    assert len(result) == len(mixed_diffs)


def test_no_rules_nothing_pruned(mixed_diffs):
    result = prune_diffs(mixed_diffs, rules=[])
    assert all(not r.pruned for r in result)


def test_no_rules_matched_rule_is_none(mixed_diffs):
    result = prune_diffs(mixed_diffs, rules=[])
    assert all(r.matched_rule is None for r in result)


def test_exact_key_match_pruned(mixed_diffs):
    rules = [PruneRule(key_pattern="LastUpdated")]
    result = prune_diffs(mixed_diffs, rules=rules)
    pruned_keys = {r.diff.key for r in result if r.pruned}
    assert pruned_keys == {"LastUpdated"}


def test_glob_key_match_pruned(mixed_diffs):
    rules = [PruneRule(key_pattern="*Password")]
    result = prune_diffs(mixed_diffs, rules=rules)
    pruned_keys = {r.diff.key for r in result if r.pruned}
    assert "DatabasePassword" in pruned_keys


def test_value_pattern_restricts_match():
    diffs = [
        KeyDiff(key="Env", baseline="prod", target="staging"),
        KeyDiff(key="Env", baseline="dev", target="test"),
    ]
    rules = [PruneRule(key_pattern="Env", value_pattern="prod")]
    result = prune_diffs(diffs, rules=rules)
    # Only the entry whose values contain "prod" should be pruned.
    assert result[0].pruned is True
    assert result[1].pruned is False


def test_matched_rule_recorded(mixed_diffs):
    rule = PruneRule(key_pattern="LastUpdated")
    result = prune_diffs(mixed_diffs, rules=[rule])
    match = next(r for r in result if r.diff.key == "LastUpdated")
    assert match.matched_rule is rule


def test_first_matching_rule_wins():
    diff = [KeyDiff(key="BucketName", baseline="a", target="b")]
    rule1 = PruneRule(key_pattern="Bucket*")
    rule2 = PruneRule(key_pattern="BucketName")
    result = prune_diffs(diff, rules=[rule1, rule2])
    assert result[0].matched_rule is rule1


# ---------------------------------------------------------------------------
# active_diffs
# ---------------------------------------------------------------------------

def test_active_diffs_excludes_pruned(mixed_diffs):
    rules = [PruneRule(key_pattern="LastUpdated")]
    pruned = prune_diffs(mixed_diffs, rules=rules)
    active = active_diffs(pruned)
    active_keys = {r.diff.key for r in active}
    assert "LastUpdated" not in active_keys


def test_active_diffs_keeps_unpruned(mixed_diffs):
    rules = [PruneRule(key_pattern="LastUpdated")]
    pruned = prune_diffs(mixed_diffs, rules=rules)
    active = active_diffs(pruned)
    assert len(active) == len(mixed_diffs) - 1


# ---------------------------------------------------------------------------
# as_dict / __str__
# ---------------------------------------------------------------------------

def test_as_dict_contains_expected_keys():
    diff = KeyDiff(key="Foo", baseline="a", target="b")
    pd = PrunedDiff(diff=diff, pruned=False)
    d = pd.as_dict()
    assert {"key", "baseline", "target", "pruned", "matched_rule"} == d.keys()


def test_str_includes_pruned_tag():
    diff = KeyDiff(key="Foo", baseline="a", target="b")
    rule = PruneRule(key_pattern="Foo")
    pd = PrunedDiff(diff=diff, pruned=True, matched_rule=rule)
    assert "[pruned]" in str(pd)


def test_str_no_tag_when_not_pruned():
    diff = KeyDiff(key="Foo", baseline="a", target="b")
    pd = PrunedDiff(diff=diff, pruned=False)
    assert "[pruned]" not in str(pd)
