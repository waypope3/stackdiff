"""Tests for stackdiff.exporter."""
from __future__ import annotations

import json
import csv
import io
from pathlib import Path

import pytest

from stackdiff.exporter import export_diff, ExportError


SAMPLE: dict = {
    "BucketName": {"baseline": "old-bucket", "target": "new-bucket", "status": "changed"},
    "Region": {"baseline": "us-east-1", "target": "us-east-1", "status": "unchanged"},
    "NewKey": {"baseline": None, "target": "value", "status": "added"},
}


def test_export_json(tmp_path: Path) -> None:
    dest = tmp_path / "out.json"
    export_diff(SAMPLE, "json", dest)
    data = json.loads(dest.read_text())
    assert isinstance(data, list)
    assert len(data) == 3
    keys = {row["key"] for row in data}
    assert keys == {"BucketName", "Region", "NewKey"}


def test_export_json_fields(tmp_path: Path) -> None:
    dest = tmp_path / "out.json"
    export_diff(SAMPLE, "json", dest)
    data = json.loads(dest.read_text())
    bucket = next(r for r in data if r["key"] == "BucketName")
    assert bucket["baseline"] == "old-bucket"
    assert bucket["target"] == "new-bucket"
    assert bucket["status"] == "changed"


def test_export_csv(tmp_path: Path) -> None:
    dest = tmp_path / "out.csv"
    export_diff(SAMPLE, "csv", dest)
    text = dest.read_text()
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    assert len(rows) == 3
    assert {r["key"] for r in rows} == {"BucketName", "Region", "NewKey"}


def test_export_csv_header(tmp_path: Path) -> None:
    dest = tmp_path / "out.csv"
    export_diff(SAMPLE, "csv", dest)
    first_line = dest.read_text().splitlines()[0]
    assert "key" in first_line
    assert "status" in first_line


def test_export_markdown(tmp_path: Path) -> None:
    dest = tmp_path / "out.md"
    export_diff(SAMPLE, "markdown", dest)
    text = dest.read_text()
    assert "| Key |" in text
    assert "BucketName" in text
    assert "changed" in text


def test_export_markdown_separator(tmp_path: Path) -> None:
    dest = tmp_path / "out.md"
    export_diff(SAMPLE, "markdown", dest)
    lines = dest.read_text().splitlines()
    assert lines[1].startswith("|---")


def test_unknown_format_raises(tmp_path: Path) -> None:
    dest = tmp_path / "out.txt"
    with pytest.raises(ExportError, match="Unknown export format"):
        export_diff(SAMPLE, "xml", dest)  # type: ignore[arg-type]


def test_unwritable_path_raises(tmp_path: Path) -> None:
    dest = tmp_path / "no_dir" / "out.json"
    with pytest.raises(ExportError, match="Could not write"):
        export_diff(SAMPLE, "json", dest)
