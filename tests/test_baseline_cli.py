"""Tests for stackdiff.baseline_cli sub-commands."""
from __future__ import annotations

import argparse
import json
import pytest

from stackdiff.baseline_cli import build_baseline_parser, _cmd_compare, _cmd_update, _cmd_list
from stackdiff.baseline import update_baseline


@pytest.fixture()
def snap_dir(tmp_path):
    d = tmp_path / "snaps"
    d.mkdir()
    return str(d)


@pytest.fixture()
def stack_file(tmp_path):
    data = {"Outputs": {"KeyA": "v1", "KeyB": "v2"}}
    p = tmp_path / "stack.json"
    p.write_text(json.dumps(data))
    return str(p)


@pytest.fixture()
def saved(snap_dir, stack_file):
    from stackdiff.parser import load_stack
    stack = load_stack(stack_file)
    update_baseline(stack, "prod", snap_dir=snap_dir)


def _ns(**kw):
    return argparse.Namespace(**kw)


def test_update_returns_zero(stack_file, snap_dir):
    ns = _ns(stack_file=stack_file, name="prod", snap_dir=snap_dir)
    assert _cmd_update(ns) == 0


def test_compare_no_diff_exit_zero(stack_file, snap_dir, saved):
    ns = _ns(stack_file=stack_file, name="prod", snap_dir=snap_dir, format="text")
    assert _cmd_compare(ns) == 0


def test_compare_with_diff_exit_one(tmp_path, snap_dir, saved):
    changed = {"Outputs": {"KeyA": "CHANGED", "KeyB": "v2"}}
    p = tmp_path / "changed.json"
    p.write_text(json.dumps(changed))
    ns = _ns(stack_file=str(p), name="prod", snap_dir=snap_dir, format="text")
    assert _cmd_compare(ns) == 1


def test_compare_missing_baseline_exit_two(stack_file, snap_dir):
    ns = _ns(stack_file=stack_file, name="ghost", snap_dir=snap_dir, format="text")
    assert _cmd_compare(ns) == 2


def test_list_empty(snap_dir, capsys):
    ns = _ns(snap_dir=snap_dir)
    _cmd_list(ns)
    out = capsys.readouterr().out
    assert "No baselines" in out


def test_list_shows_names(snap_dir, stack_file, saved, capsys):
    ns = _ns(snap_dir=snap_dir)
    _cmd_list(ns)
    out = capsys.readouterr().out
    assert "prod" in out
