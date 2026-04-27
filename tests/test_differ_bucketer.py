"""Tests for stackdiff.differ_bucketer."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_bucketer import (
    BucketSpec,
    BucketedDiff,
    BucketResult,
    DEFAULT_BUCKETS,
    bucket_diffs,
)


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="short_key", baseline_value="abc", target_value="xyz"),
        KeyDiff(key="medium_key", baseline_value="x" * 50, target_value="x" * 50),
        KeyDiff(key="long_key", baseline_value=None, target_value="y" * 200),
        KeyDiff(key="removed_key", baseline_value="gone", target_value=None),
        KeyDiff(key="unchanged_key", baseline_value="same", target_value="same"),
    ]


def test_returns_bucket_result(mixed_diffs):
    result = bucket_diffs(mixed_diffs)
    assert isinstance(result, BucketResult)


def test_diffs_length_matches_input(mixed_diffs):
    result = bucket_diffs(mixed_diffs)
    assert len(result.diffs) == len(mixed_diffs)


def test_all_diffs_are_bucketed_diff_instances(mixed_diffs):
    result = bucket_diffs(mixed_diffs)
    assert all(isinstance(d, BucketedDiff) for d in result.diffs)


def test_short_value_in_short_bucket(mixed_diffs):
    result = bucket_diffs(mixed_diffs)
    short = next(d for d in result.diffs if d.key == "short_key")
    assert short.bucket == "short"


def test_medium_value_in_medium_bucket(mixed_diffs):
    result = bucket_diffs(mixed_diffs)
    medium = next(d for d in result.diffs if d.key == "medium_key")
    assert medium.bucket == "medium"


def test_long_value_in_long_bucket(mixed_diffs):
    result = bucket_diffs(mixed_diffs)
    long_ = next(d for d in result.diffs if d.key == "long_key")
    assert long_.bucket == "long"


def test_removed_key_uses_baseline_for_bucket(mixed_diffs):
    result = bucket_diffs(mixed_diffs)
    removed = next(d for d in result.diffs if d.key == "removed_key")
    # baseline_value="gone" (4 chars) -> short
    assert removed.bucket == "short"


def test_changed_flag_set_when_values_differ(mixed_diffs):
    result = bucket_diffs(mixed_diffs)
    changed = next(d for d in result.diffs if d.key == "short_key")
    assert changed.changed is True


def test_changed_flag_clear_when_values_equal(mixed_diffs):
    result = bucket_diffs(mixed_diffs)
    unchanged = next(d for d in result.diffs if d.key == "unchanged_key")
    assert unchanged.changed is False


def test_bucket_map_keys_match_specs(mixed_diffs):
    result = bucket_diffs(mixed_diffs)
    assert set(result.buckets.keys()) == {s.name for s in DEFAULT_BUCKETS}


def test_custom_specs():
    specs = [BucketSpec("tiny", 0, 5), BucketSpec("big", 5, None)]
    diffs = [
        KeyDiff(key="a", baseline_value="hi", target_value="hi"),
        KeyDiff(key="b", baseline_value="hello world", target_value="hello world"),
    ]
    result = bucket_diffs(diffs, specs=specs)
    assert result.diffs[0].bucket == "tiny"
    assert result.diffs[1].bucket == "big"


def test_as_dict_contains_expected_keys(mixed_diffs):
    result = bucket_diffs(mixed_diffs)
    d = result.as_dict()
    assert "buckets" in d
    assert "total" in d
    assert d["total"] == len(mixed_diffs)


def test_str_representation(mixed_diffs):
    result = bucket_diffs(mixed_diffs)
    for bd in result.diffs:
        s = str(bd)
        assert bd.key in s
        assert bd.bucket in s
