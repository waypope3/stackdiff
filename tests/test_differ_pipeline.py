"""Tests for stackdiff.differ_pipeline."""
import json
import pathlib
import pytest

from stackdiff.differ_pipeline import PipelineOptions, PipelineResult, run_diff_pipeline
from stackdiff.differ import Status
from stackdiff.sorter import SortOrder


@pytest.fixture()
def stack_dir(tmp_path: pathlib.Path):
    def _write(name: str, outputs: dict) -> str:
        p = tmp_path / name
        p.write_text(json.dumps({"Outputs": outputs}))
        return str(p)
    return _write


def test_returns_pipeline_result(stack_dir):
    b = stack_dir("b.json", {"KeyA": "val1"})
    t = stack_dir("t.json", {"KeyA": "val1"})
    result = run_diff_pipeline(b, t)
    assert isinstance(result, PipelineResult)


def test_changed_key_detected(stack_dir):
    b = stack_dir("b.json", {"KeyA": "old"})
    t = stack_dir("t.json", {"KeyA": "new"})
    result = run_diff_pipeline(b, t)
    assert any(d.status == Status.CHANGED for d in result.diffs)


def test_added_key_detected(stack_dir):
    b = stack_dir("b.json", {})
    t = stack_dir("t.json", {"KeyA": "new"})
    result = run_diff_pipeline(b, t)
    assert any(d.status == Status.ADDED for d in result.diffs)


def test_removed_key_detected(stack_dir):
    b = stack_dir("b.json", {"KeyA": "old"})
    t = stack_dir("t.json", {})
    result = run_diff_pipeline(b, t)
    assert any(d.status == Status.REMOVED for d in result.diffs)


def test_include_filter_applied(stack_dir):
    b = stack_dir("b.json", {"KeyA": "1", "KeyB": "2"})
    t = stack_dir("t.json", {"KeyA": "1", "KeyB": "9"})
    opts = PipelineOptions(include=["KeyA"])
    result = run_diff_pipeline(b, t, opts)
    keys = [d.key for d in result.diffs]
    assert "KeyA" in keys
    assert "KeyB" not in keys


def test_exclude_filter_applied(stack_dir):
    b = stack_dir("b.json", {"KeyA": "1", "KeyB": "2"})
    t = stack_dir("t.json", {"KeyA": "1", "KeyB": "9"})
    opts = PipelineOptions(exclude=["KeyB"])
    result = run_diff_pipeline(b, t, opts)
    keys = [d.key for d in result.diffs]
    assert "KeyB" not in keys


def test_sources_recorded(stack_dir):
    b = stack_dir("b.json", {})
    t = stack_dir("t.json", {})
    result = run_diff_pipeline(b, t)
    assert result.baseline_source == b
    assert result.target_source == t


def test_truncation_applied(stack_dir):
    long_val = "x" * 200
    b = stack_dir("b.json", {"K": long_val})
    t = stack_dir("t.json", {"K": long_val})
    opts = PipelineOptions(truncate=20)
    result = run_diff_pipeline(b, t, opts)
    for d in result.diffs:
        if d.baseline_value is not None:
            assert len(d.baseline_value) <= 23  # 20 + len("...")
