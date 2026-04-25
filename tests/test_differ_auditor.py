"""Tests for stackdiff.differ_auditor."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_auditor import (
    AuditEntry,
    AuditRecord,
    _status,
    audit_diffs,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="VpcId", baseline_value="vpc-aaa", target_value="vpc-bbb"),
        KeyDiff(key="SubnetId", baseline_value=None, target_value="subnet-xyz"),
        KeyDiff(key="OldKey", baseline_value="v1", target_value=None),
        KeyDiff(key="Region", baseline_value="us-east-1", target_value="us-east-1"),
    ]


# ---------------------------------------------------------------------------
# _status helper
# ---------------------------------------------------------------------------

def test_status_changed():
    d = KeyDiff(key="k", baseline_value="a", target_value="b")
    assert _status(d) == "changed"


def test_status_added():
    d = KeyDiff(key="k", baseline_value=None, target_value="b")
    assert _status(d) == "added"


def test_status_removed():
    d = KeyDiff(key="k", baseline_value="a", target_value=None)
    assert _status(d) == "removed"


def test_status_unchanged():
    d = KeyDiff(key="k", baseline_value="a", target_value="a")
    assert _status(d) == "unchanged"


# ---------------------------------------------------------------------------
# audit_diffs
# ---------------------------------------------------------------------------

def test_returns_audit_record(mixed_diffs):
    record = audit_diffs(mixed_diffs)
    assert isinstance(record, AuditRecord)


def test_entry_count_matches_input(mixed_diffs):
    record = audit_diffs(mixed_diffs)
    assert len(record.entries) == len(mixed_diffs)


def test_entries_are_audit_entry_instances(mixed_diffs):
    record = audit_diffs(mixed_diffs)
    assert all(isinstance(e, AuditEntry) for e in record.entries)


def test_changed_status_recorded(mixed_diffs):
    record = audit_diffs(mixed_diffs)
    entry = next(e for e in record.entries if e.key == "VpcId")
    assert entry.status == "changed"
    assert entry.baseline_value == "vpc-aaa"
    assert entry.target_value == "vpc-bbb"


def test_added_status_recorded(mixed_diffs):
    record = audit_diffs(mixed_diffs)
    entry = next(e for e in record.entries if e.key == "SubnetId")
    assert entry.status == "added"
    assert entry.baseline_value is None


def test_removed_status_recorded(mixed_diffs):
    record = audit_diffs(mixed_diffs)
    entry = next(e for e in record.entries if e.key == "OldKey")
    assert entry.status == "removed"
    assert entry.target_value is None


def test_sources_stored(mixed_diffs):
    record = audit_diffs(mixed_diffs, baseline_source="s3://b/f", target_source="s3://b/g")
    assert record.baseline_source == "s3://b/f"
    assert record.target_source == "s3://b/g"


def test_run_at_is_utc_iso(mixed_diffs):
    record = audit_diffs(mixed_diffs)
    assert record.run_at.endswith("Z")


def test_as_dict_has_expected_keys(mixed_diffs):
    d = audit_diffs(mixed_diffs).as_dict()
    assert set(d.keys()) == {"run_at", "user", "hostname",
                              "baseline_source", "target_source", "entries"}


def test_str_contains_user(mixed_diffs):
    record = audit_diffs(mixed_diffs)
    assert "user=" in str(record)
