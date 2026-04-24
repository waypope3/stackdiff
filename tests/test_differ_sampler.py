"""Tests for stackdiff.differ_sampler."""
import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_sampler import (
    SampleOptions,
    SampledDiff,
    sample_diffs,
)


def _d(key: str, base: str, target: str) -> KeyDiff:
    return KeyDiff(key=key, baseline_value=base, target_value=target)


@pytest.fixture()
def mixed_diffs():
    return [
        _d("vpc_id", "vpc-aaa", "vpc-bbb"),        # changed
        _d("region", "us-east-1", "us-east-1"),    # unchanged
        _d("env", "staging", "prod"),               # changed
        _d("owner", "alice", "alice"),              # unchanged
        _d("bucket", "bkt-1", "bkt-1"),            # unchanged
    ]


def test_returns_sampled_diff_instances(mixed_diffs):
    opts = SampleOptions(n=5, seed=0)
    result = sample_diffs(mixed_diffs, opts)
    assert all(isinstance(r, SampledDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    opts = SampleOptions(n=5, seed=0)
    result = sample_diffs(mixed_diffs, opts)
    assert len(result) == len(mixed_diffs)


def test_all_included_when_n_exceeds_total(mixed_diffs):
    opts = SampleOptions(n=100, seed=0)
    result = sample_diffs(mixed_diffs, opts)
    assert all(r.included for r in result)


def test_changed_first_keeps_all_changed(mixed_diffs):
    opts = SampleOptions(n=2, seed=0, changed_first=True)
    result = sample_diffs(mixed_diffs, opts)
    changed = [r for r in result if r.changed]
    assert all(c.included for c in changed)


def test_n_zero_excludes_all(mixed_diffs):
    opts = SampleOptions(n=0, seed=0)
    result = sample_diffs(mixed_diffs, opts)
    assert all(not r.included for r in result)


def test_negative_n_raises():
    with pytest.raises(ValueError, match=">= 0"):
        sample_diffs([], SampleOptions(n=-1))


def test_sample_index_sequential(mixed_diffs):
    opts = SampleOptions(n=3, seed=42)
    result = sample_diffs(mixed_diffs, opts)
    indices = [r.sample_index for r in result if r.included]
    assert indices == list(range(len(indices)))


def test_excluded_have_minus_one_index(mixed_diffs):
    opts = SampleOptions(n=2, seed=0)
    result = sample_diffs(mixed_diffs, opts)
    for r in result:
        if not r.included:
            assert r.sample_index == -1


def test_changed_flag_correct(mixed_diffs):
    opts = SampleOptions(n=10, seed=0)
    result = sample_diffs(mixed_diffs, opts)
    for r in result:
        expected = r.baseline_value != r.target_value
        assert r.changed == expected


def test_seed_reproducible(mixed_diffs):
    opts1 = SampleOptions(n=3, seed=7)
    opts2 = SampleOptions(n=3, seed=7)
    r1 = [r.key for r in sample_diffs(mixed_diffs, opts1) if r.included]
    r2 = [r.key for r in sample_diffs(mixed_diffs, opts2) if r.included]
    assert r1 == r2


def test_as_dict_keys(mixed_diffs):
    opts = SampleOptions(n=5, seed=0)
    result = sample_diffs(mixed_diffs, opts)
    d = result[0].as_dict()
    assert set(d.keys()) == {
        "key", "baseline_value", "target_value", "changed", "included", "sample_index"
    }
