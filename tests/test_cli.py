"""Tests for the stackdiff CLI entry point."""

import json
import pytest

from stackdiff.cli import main


@pytest.fixture()
def baseline_file(tmp_path):
    data = {"outputs": {"region": "us-east-1", "bucket": "my-bucket"}}
    p = tmp_path / "baseline.json"
    p.write_text(json.dumps(data))
    return str(p)


@pytest.fixture()
def target_same(tmp_path):
    data = {"outputs": {"region": "us-east-1", "bucket": "my-bucket"}}
    p = tmp_path / "target_same.json"
    p.write_text(json.dumps(data))
    return str(p)


@pytest.fixture()
def target_changed(tmp_path):
    data = {"outputs": {"region": "eu-west-1", "bucket": "other-bucket"}}
    p = tmp_path / "target_changed.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_no_diff_exit_zero(baseline_file, target_same):
    assert main([baseline_file, target_same]) == 0


def test_diff_exit_zero_without_flag(baseline_file, target_changed):
    assert main([baseline_file, target_changed]) == 0


def test_diff_exit_one_with_flag(baseline_file, target_changed):
    assert main([baseline_file, target_changed, "--exit-code"]) == 1


def test_no_diff_exit_zero_with_flag(baseline_file, target_same):
    assert main([baseline_file, target_same, "--exit-code"]) == 0


def test_missing_file_returns_2(baseline_file):
    assert main([baseline_file, "nonexistent.json"]) == 2


def test_no_colour_flag_accepted(baseline_file, target_changed):
    code = main([baseline_file, target_changed, "--no-colour"])
    assert code == 0


def test_invalid_file_returns_2(tmp_path, baseline_file):
    bad = tmp_path / "bad.json"
    bad.write_text("not: valid: json: yaml: !!!")
    assert main([baseline_file, str(bad)]) == 2
