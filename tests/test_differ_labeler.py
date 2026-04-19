import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_labeler import label_diffs, LabeledDiff
from stackdiff.label_formatter import format_labeled, format_labeled_table


@pytest.fixture
def mixed_diffs():
    return [
        KeyDiff(key="Alpha", baseline_value="old", target_value="new"),
        KeyDiff(key="Beta", baseline_value=None, target_value="added"),
        KeyDiff(key="Gamma", baseline_value="gone", target_value=None),
        KeyDiff(key="Delta", baseline_value="same", target_value="same"),
    ]


def test_label_changed(mixed_diffs):
    labeled = label_diffs(mixed_diffs)
    assert labeled[0].status == "changed"
    assert labeled[0].label == "Modified"


def test_label_added(mixed_diffs):
    labeled = label_diffs(mixed_diffs)
    assert labeled[1].status == "added"
    assert labeled[1].label == "Added"


def test_label_removed(mixed_diffs):
    labeled = label_diffs(mixed_diffs)
    assert labeled[2].status == "removed"
    assert labeled[2].label == "Removed"


def test_label_unchanged(mixed_diffs):
    labeled = label_diffs(mixed_diffs)
    assert labeled[3].status == "unchanged"
    assert labeled[3].label == "Unchanged"


def test_hint_populated(mixed_diffs):
    labeled = label_diffs(mixed_diffs)
    for d in labeled:
        assert d.hint != ""


def test_custom_labels(mixed_diffs):
    labeled = label_diffs(mixed_diffs, custom_labels={"changed": "Updated"})
    assert labeled[0].label == "Updated"
    assert labeled[1].label == "Added"  # unchanged


def test_as_dict(mixed_diffs):
    labeled = label_diffs(mixed_diffs)
    d = labeled[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "status", "label", "hint"}


def test_format_labeled_empty():
    assert format_labeled([]) == "No differences."


def test_format_labeled_contains_key(mixed_diffs):
    labeled = label_diffs(mixed_diffs)
    out = format_labeled(labeled)
    assert "Alpha" in out
    assert "Beta" in out


def test_format_labeled_hints(mixed_diffs):
    labeled = label_diffs(mixed_diffs)
    out = format_labeled(labeled, show_hints=True)
    assert "#" in out


def test_format_labeled_table_header(mixed_diffs):
    labeled = label_diffs(mixed_diffs)
    out = format_labeled_table(labeled)
    assert "KEY" in out
    assert "STATUS" in out


def test_format_labeled_table_empty():
    assert format_labeled_table([]) == "No differences."
