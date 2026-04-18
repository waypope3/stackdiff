"""Tests for stackdiff.profiler."""
import time

import pytest

from stackdiff.profiler import Profile, Profiler, Span


def test_record_span():
    p = Profile()
    p.record("load", 0.05)
    assert len(p.spans) == 1
    assert p.spans[0].name == "load"
    assert p.spans[0].elapsed == 0.05


def test_total():
    p = Profile()
    p.record("a", 0.1)
    p.record("b", 0.2)
    assert abs(p.total() - 0.3) < 1e-9


def test_summary_keys():
    p = Profile()
    p.record("x", 0.123456)
    p.record("y", 0.654321)
    s = p.summary()
    assert set(s.keys()) == {"x", "y"}


def test_slowest():
    p = Profile()
    p.record("fast", 0.01)
    p.record("slow", 0.99)
    assert p.slowest().name == "slow"


def test_slowest_empty():
    assert Profile().slowest() is None


def test_profiler_start_stop():
    pr = Profiler()
    pr.start("stage1")
    time.sleep(0.01)
    pr.stop()
    assert len(pr.profile.spans) == 1
    assert pr.profile.spans[0].name == "stage1"
    assert pr.profile.spans[0].elapsed >= 0.01


def test_profiler_stop_without_start():
    pr = Profiler()
    with pytest.raises(RuntimeError):
        pr.stop()


def test_profiler_stage_context_manager():
    pr = Profiler()
    with pr.stage("ctx"):
        time.sleep(0.005)
    assert pr.profile.spans[0].name == "ctx"
    assert pr.profile.spans[0].elapsed >= 0.005


def test_profiler_multiple_stages():
    pr = Profiler()
    for name in ("a", "b", "c"):
        with pr.stage(name):
            pass
    assert [s.name for s in pr.profile.spans] == ["a", "b", "c"]
    assert pr.profile.total() >= 0
