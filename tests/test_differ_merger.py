import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_merger import merge_diffs, MergeResult, MergedDiff


def _diff(key, old, new):
    return KeyDiff(key=key, old=old, new=new)


@pytest.fixture
def baseline():
    return [
        _diff("KeyA", "v1", "v2"),
        _diff("KeyB", "x", "x"),
    ]


@pytest.fixture
def target():
    return [
        _diff("KeyA", "v1", "v3"),
        _diff("KeyC", None, "new"),
    ]


def test_all_keys_present(baseline, target):
    result = merge_diffs(baseline, target)
    keys = [m.key for m in result.merged]
    assert "KeyA" in keys
    assert "KeyB" in keys
    assert "KeyC" in keys


def test_diverged_status(baseline, target):
    result = merge_diffs(baseline, target)
    a = next(m for m in result.merged if m.key == "KeyA")
    assert a.status == "diverged"


def test_only_in_baseline(baseline, target):
    result = merge_diffs(baseline, target)
    b = next(m for m in result.merged if m.key == "KeyB")
    assert b.status == "only_in_baseline"


def test_new_in_target(baseline, target):
    result = merge_diffs(baseline, target)
    c = next(m for m in result.merged if m.key == "KeyC")
    assert c.status == "new_in_target"


def test_same_status():
    b = [_diff("KeyX", "a", "b")]
    t = [_diff("KeyX", "a", "b")]
    result = merge_diffs(b, t)
    assert result.merged[0].status == "same"


def test_has_divergence_true(baseline, target):
    result = merge_diffs(baseline, target)
    assert result.has_divergence() is True


def test_has_divergence_false():
    b = [_diff("KeyX", "a", "b")]
    t = [_diff("KeyX", "a", "b")]
    result = merge_diffs(b, t)
    assert result.has_divergence() is False


def test_by_status(baseline, target):
    result = merge_diffs(baseline, target)
    assert len(result.by_status("diverged")) == 1
    assert len(result.by_status("only_in_baseline")) == 1
    assert len(result.by_status("new_in_target")) == 1


def test_empty_inputs():
    result = merge_diffs([], [])
    assert result.merged == []
    assert result.has_divergence() is False
