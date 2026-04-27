"""Tests for stackdiff.differ_evolver."""
import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_evolver import EvolvedDiff, _detect_trend, evolve_diffs


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _d(key: str, old: str | None, new: str | None) -> KeyDiff:
    return KeyDiff(key=key, old_value=old, new_value=new)


@pytest.fixture()
def three_snapshots():
    snap1 = [_d("VpcId", None, "vpc-aaa"), _d("SubnetId", None, "sub-111")]
    snap2 = [_d("VpcId", "vpc-aaa", "vpc-bbb"), _d("SubnetId", "sub-111", "sub-111")]
    snap3 = [_d("VpcId", "vpc-bbb", "vpc-ccc"), _d("SubnetId", "sub-111", "sub-222")]
    return [snap1, snap2, snap3]


# ---------------------------------------------------------------------------
# _detect_trend
# ---------------------------------------------------------------------------

def test_trend_stable_single_value():
    assert _detect_trend(["abc"]) == "stable"


def test_trend_stable_no_changes():
    assert _detect_trend(["abc", "abc", "abc"]) == "stable"


def test_trend_volatile_all_change():
    assert _detect_trend(["a", "b", "c", "d"]) == "volatile"


def test_trend_growing():
    assert _detect_trend(["a", "ab", "abc", "abcd"]) == "growing"


def test_trend_shrinking():
    assert _detect_trend(["abcd", "abc", "ab", "a"]) == "shrinking"


def test_trend_empty_history():
    assert _detect_trend([]) == "stable"


# ---------------------------------------------------------------------------
# evolve_diffs
# ---------------------------------------------------------------------------

def test_empty_snapshots_returns_empty():
    assert evolve_diffs([]) == []


def test_returns_evolved_diff_instances(three_snapshots):
    result = evolve_diffs(three_snapshots)
    assert all(isinstance(r, EvolvedDiff) for r in result)


def test_same_length_as_unique_keys(three_snapshots):
    result = evolve_diffs(three_snapshots)
    assert len(result) == 2  # VpcId, SubnetId


def test_changed_flag_set_when_values_differ(three_snapshots):
    result = {r.key: r for r in evolve_diffs(three_snapshots)}
    assert result["VpcId"].changed is True


def test_unchanged_flag_clear_for_stable_key():
    snap1 = [_d("Bucket", None, "my-bucket")]
    snap2 = [_d("Bucket", "my-bucket", "my-bucket")]
    result = evolve_diffs([snap1, snap2])
    assert result[0].changed is False


def test_change_count_correct(three_snapshots):
    result = {r.key: r for r in evolve_diffs(three_snapshots)}
    assert result["VpcId"].change_count == 2
    assert result["SubnetId"].change_count == 1


def test_first_and_last_seen(three_snapshots):
    result = {r.key: r for r in evolve_diffs(three_snapshots)}
    assert result["VpcId"].first_seen == "vpc-aaa"
    assert result["VpcId"].last_seen == "vpc-ccc"


def test_key_absent_in_later_snapshot_has_none():
    snap1 = [_d("OldKey", None, "v1")]
    snap2 = []  # key disappears
    result = evolve_diffs([snap1, snap2])
    assert result[0].history == ["v1", None]


def test_as_dict_keys(three_snapshots):
    r = evolve_diffs(three_snapshots)[0]
    d = r.as_dict()
    assert set(d.keys()) == {
        "key", "history", "changed", "first_seen", "last_seen",
        "change_count", "trend",
    }


def test_history_length_equals_snapshot_count(three_snapshots):
    result = evolve_diffs(three_snapshots)
    for r in result:
        assert len(r.history) == 3
