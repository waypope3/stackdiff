"""Tests for stackdiff.differ_tracer."""
import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_tracer import TraceEntry, TracedDiff, trace_diffs


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def two_snapshots():
    snap1 = [
        KeyDiff(key="VpcId", baseline="vpc-aaa", target="vpc-aaa"),
        KeyDiff(key="SubnetId", baseline="subnet-111", target="subnet-222"),
    ]
    snap2 = [
        KeyDiff(key="VpcId", baseline="vpc-aaa", target="vpc-bbb"),
        KeyDiff(key="SubnetId", baseline="subnet-222", target="subnet-222"),
        KeyDiff(key="BucketName", baseline=None, target="my-bucket"),
    ]
    return [("snap-1", snap1), ("snap-2", snap2)]


# ---------------------------------------------------------------------------
# trace_diffs
# ---------------------------------------------------------------------------

def test_returns_traced_diff_instances(two_snapshots):
    result = trace_diffs(two_snapshots)
    assert all(isinstance(r, TracedDiff) for r in result)


def test_unique_keys_collected(two_snapshots):
    result = trace_diffs(two_snapshots)
    keys = [r.key for r in result]
    assert sorted(keys) == sorted(["VpcId", "SubnetId", "BucketName"])


def test_history_length_reflects_appearances(two_snapshots):
    result = trace_diffs(two_snapshots)
    by_key = {r.key: r for r in result}
    assert len(by_key["VpcId"].history) == 2
    assert len(by_key["BucketName"].history) == 1


def test_changed_flag_set_when_values_differ(two_snapshots):
    result = trace_diffs(two_snapshots)
    by_key = {r.key: r for r in result}
    # SubnetId changed in snap-1 (111->222), unchanged in snap-2
    subnet = by_key["SubnetId"]
    assert subnet.history[0].changed is True
    assert subnet.history[1].changed is False


def test_ever_changed_true_if_any_entry_changed(two_snapshots):
    result = trace_diffs(two_snapshots)
    by_key = {r.key: r for r in result}
    assert by_key["VpcId"].ever_changed is True
    assert by_key["SubnetId"].ever_changed is True


def test_ever_changed_false_when_always_stable():
    snaps = [
        ("s1", [KeyDiff(key="Foo", baseline="bar", target="bar")]),
        ("s2", [KeyDiff(key="Foo", baseline="bar", target="bar")]),
    ]
    result = trace_diffs(snaps)
    assert result[0].ever_changed is False


def test_total_changes_count(two_snapshots):
    result = trace_diffs(two_snapshots)
    by_key = {r.key: r for r in result}
    assert by_key["VpcId"].total_changes == 1


def test_latest_returns_last_entry(two_snapshots):
    result = trace_diffs(two_snapshots)
    by_key = {r.key: r for r in result}
    assert by_key["VpcId"].latest.snapshot_id == "snap-2"


def test_empty_snapshots_returns_empty():
    assert trace_diffs([]) == []


def test_as_dict_contains_required_keys(two_snapshots):
    result = trace_diffs(two_snapshots)
    d = result[0].as_dict()
    assert {"key", "total_changes", "ever_changed", "history"} <= d.keys()


def test_trace_entry_as_dict():
    entry = TraceEntry(
        snapshot_id="s1", baseline_value="old", target_value="new", changed=True
    )
    d = entry.as_dict()
    assert d["snapshot_id"] == "s1"
    assert d["changed"] is True


def test_str_repr():
    td = TracedDiff(key="MyKey", history=[])
    assert "MyKey" in str(td)
