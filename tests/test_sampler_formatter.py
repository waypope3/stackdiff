"""Tests for stackdiff.sampler_formatter."""
from stackdiff.differ import KeyDiff
from stackdiff.differ_sampler import SampleOptions, sample_diffs
from stackdiff.sampler_formatter import format_sampled, format_sampled_table


def _make_diffs():
    raw = [
        KeyDiff(key="vpc_id", baseline_value="old", target_value="new"),
        KeyDiff(key="region", baseline_value="us-east-1", target_value="us-east-1"),
        KeyDiff(key="env", baseline_value="staging", target_value="prod"),
        KeyDiff(key="owner", baseline_value="alice", target_value="alice"),
    ]
    opts = SampleOptions(n=3, seed=0, changed_first=True)
    return sample_diffs(raw, opts)


def test_format_sampled_contains_summary():
    diffs = _make_diffs()
    output = format_sampled(diffs)
    assert "included" in output
    assert "excluded" in output


def test_format_sampled_shows_included_keys():
    diffs = _make_diffs()
    output = format_sampled(diffs)
    included_keys = [d.key for d in diffs if d.included]
    for key in included_keys:
        assert key in output


def test_format_sampled_excluded_hidden_by_default():
    diffs = _make_diffs()
    excluded_keys = [d.key for d in diffs if not d.included]
    output = format_sampled(diffs, show_excluded=False)
    for key in excluded_keys:
        assert key not in output


def test_format_sampled_excluded_shown_when_requested():
    diffs = _make_diffs()
    excluded_keys = [d.key for d in diffs if not d.included]
    if not excluded_keys:
        return  # nothing to assert
    output = format_sampled(diffs, show_excluded=True)
    for key in excluded_keys:
        assert key in output


def test_format_sampled_table_contains_header():
    diffs = _make_diffs()
    output = format_sampled_table(diffs)
    assert "KEY" in output
    assert "STATUS" in output


def test_format_sampled_table_no_included_returns_placeholder():
    from stackdiff.differ_sampler import SampledDiff
    empty = [
        SampledDiff(
            key="k", baseline_value="a", target_value="b",
            changed=True, included=False, sample_index=-1,
        )
    ]
    output = format_sampled_table(empty)
    assert "no sampled" in output


def test_format_sampled_table_shows_changed_key():
    diffs = _make_diffs()
    output = format_sampled_table(diffs)
    changed = [d for d in diffs if d.changed and d.included]
    for d in changed:
        assert d.key in output
