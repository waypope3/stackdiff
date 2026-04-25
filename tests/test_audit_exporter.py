"""Tests for stackdiff.audit_exporter."""
from __future__ import annotations

import csv
import io
import json

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_auditor import audit_diffs
from stackdiff.audit_exporter import AuditExportError, export_audit


@pytest.fixture()
def record():
    diffs = [
        KeyDiff(key="VpcId", baseline_value="vpc-aaa", target_value="vpc-bbb"),
        KeyDiff(key="NewKey", baseline_value=None, target_value="hello"),
        KeyDiff(key="Gone", baseline_value="bye", target_value=None),
        KeyDiff(key="Same", baseline_value="x", target_value="x"),
    ]
    return audit_diffs(diffs, baseline_source="local/base.json", target_source="local/target.json")


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------

def test_export_json_is_valid_json(record):
    raw = export_audit(record, fmt="json")
    data = json.loads(raw)
    assert isinstance(data, dict)


def test_export_json_top_level_keys(record):
    data = json.loads(export_audit(record, fmt="json"))
    assert "run_at" in data
    assert "entries" in data


def test_export_json_entry_count(record):
    data = json.loads(export_audit(record, fmt="json"))
    assert len(data["entries"]) == 4


def test_export_json_changed_entry(record):
    data = json.loads(export_audit(record, fmt="json"))
    entry = next(e for e in data["entries"] if e["key"] == "VpcId")
    assert entry["status"] == "changed"


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def test_export_csv_is_parseable(record):
    raw = export_audit(record, fmt="csv")
    reader = csv.DictReader(io.StringIO(raw))
    rows = list(reader)
    assert len(rows) == 4


def test_export_csv_header_columns(record):
    raw = export_audit(record, fmt="csv")
    reader = csv.DictReader(io.StringIO(raw))
    assert "key" in reader.fieldnames
    assert "status" in reader.fieldnames
    assert "baseline_value" in reader.fieldnames
    assert "target_value" in reader.fieldnames


def test_export_csv_sources_in_every_row(record):
    raw = export_audit(record, fmt="csv")
    reader = csv.DictReader(io.StringIO(raw))
    for row in reader:
        assert row["baseline_source"] == "local/base.json"
        assert row["target_source"] == "local/target.json"


# ---------------------------------------------------------------------------
# Unknown format
# ---------------------------------------------------------------------------

def test_unknown_format_raises(record):
    with pytest.raises(AuditExportError, match="xml"):
        export_audit(record, fmt="xml")  # type: ignore[arg-type]
