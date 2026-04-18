"""Tests for stackdiff.snapshot."""
import pytest
from pathlib import Path

from stackdiff.differ import KeyDiff
from stackdiff.snapshot import (
    SnapshotError,
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path / "snaps"


@pytest.fixture()
def sample_result():
    return {
        "KeyA": KeyDiff(baseline="old", target="new", status="changed"),
        "KeyB": KeyDiff(baseline="same", target="same", status="unchanged"),
        "KeyC": KeyDiff(baseline=None, target="added", status="added"),
    }


def test_save_creates_file(snap_dir, sample_result):
    path = save_snapshot(sample_result, "prod", snap_dir)
    assert path.exists()
    assert path.suffix == ".json"


def test_roundtrip(snap_dir, sample_result):
    save_snapshot(sample_result, "prod", snap_dir)
    loaded = load_snapshot("prod", snap_dir)
    assert set(loaded.keys()) == set(sample_result.keys())
    assert loaded["KeyA"].status == "changed"
    assert loaded["KeyA"].baseline == "old"
    assert loaded["KeyA"].target == "new"
    assert loaded["KeyC"].baseline is None


def test_load_missing_raises(snap_dir):
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot("ghost", snap_dir)


def test_list_empty(snap_dir):
    assert list_snapshots(snap_dir) == []


def test_list_snapshots(snap_dir, sample_result):
    save_snapshot(sample_result, "alpha", snap_dir)
    save_snapshot(sample_result, "beta", snap_dir)
    names = list_snapshots(snap_dir)
    assert "alpha" in names
    assert "beta" in names


def test_delete_existing(snap_dir, sample_result):
    save_snapshot(sample_result, "temp", snap_dir)
    assert delete_snapshot("temp", snap_dir) is True
    assert "temp" not in list_snapshots(snap_dir)


def test_delete_missing(snap_dir):
    assert delete_snapshot("nope", snap_dir) is False


def test_name_with_slashes(snap_dir, sample_result):
    save_snapshot(sample_result, "env/prod", snap_dir)
    loaded = load_snapshot("env/prod", snap_dir)
    assert "KeyA" in loaded
