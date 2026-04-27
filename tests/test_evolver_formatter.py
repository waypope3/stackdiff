"""Tests for stackdiff.evolver_formatter."""
from stackdiff.differ import KeyDiff
from stackdiff.differ_evolver import evolve_diffs
from stackdiff.evolver_formatter import format_evolved, format_evolved_table


def _d(key, old, new):
    return KeyDiff(key=key, old_value=old, new_value=new)


def _make_evolveds():
    snap1 = [_d("VpcId", None, "vpc-111"), _d("Region", None, "us-east-1")]
    snap2 = [_d("VpcId", "vpc-111", "vpc-222"), _d("Region", "us-east-1", "us-east-1")]
    return evolve_diffs([snap1, snap2])


# ---------------------------------------------------------------------------
# format_evolved
# ---------------------------------------------------------------------------

def test_format_evolved_contains_changed_key():
    evolveds = _make_evolveds()
    out = format_evolved(evolveds)
    assert "VpcId" in out


def test_format_evolved_hides_stable_by_default():
    evolveds = _make_evolveds()
    out = format_evolved(evolveds)
    assert "Region" not in out


def test_format_evolved_shows_stable_when_requested():
    evolveds = _make_evolveds()
    out = format_evolved(evolveds, show_stable=True)
    assert "Region" in out


def test_format_evolved_shows_change_count():
    evolveds = _make_evolveds()
    out = format_evolved(evolveds)
    assert "changes=1" in out


def test_format_evolved_shows_trend():
    evolveds = _make_evolveds()
    out = format_evolved(evolveds)
    assert "trend=" in out


def test_format_evolved_no_changes_message():
    snap1 = [_d("Stable", None, "x")]
    snap2 = [_d("Stable", "x", "x")]
    evolveds = evolve_diffs([snap1, snap2])
    out = format_evolved(evolveds)
    assert "no evolution" in out


# ---------------------------------------------------------------------------
# format_evolved_table
# ---------------------------------------------------------------------------

def test_format_evolved_table_contains_header():
    evolveds = _make_evolveds()
    out = format_evolved_table(evolveds)
    assert "KEY" in out
    assert "CHANGES" in out
    assert "TREND" in out


def test_format_evolved_table_shows_changed_key():
    evolveds = _make_evolveds()
    out = format_evolved_table(evolveds)
    assert "VpcId" in out


def test_format_evolved_table_hides_stable_by_default():
    evolveds = _make_evolveds()
    out = format_evolved_table(evolveds)
    assert "Region" not in out


def test_format_evolved_table_shows_stable_when_requested():
    evolveds = _make_evolveds()
    out = format_evolved_table(evolveds, show_stable=True)
    assert "Region" in out


def test_format_evolved_table_no_changes_message():
    snap1 = [_d("K", None, "v")]
    snap2 = [_d("K", "v", "v")]
    evolveds = evolve_diffs([snap1, snap2])
    out = format_evolved_table(evolveds)
    assert "no evolution" in out
