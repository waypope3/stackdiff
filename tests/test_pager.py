"""Tests for stackdiff.pager."""
from __future__ import annotations

import os
from unittest.mock import patch, MagicMock

import pytest

from stackdiff.pager import should_page, page_output


SHORT_TEXT = "line\n" * 5
LONG_TEXT = "line\n" * 100


# ---------------------------------------------------------------------------
# should_page
# ---------------------------------------------------------------------------

def test_short_text_no_page():
    assert should_page(SHORT_TEXT, threshold=40) is False


def test_long_text_page():
    assert should_page(LONG_TEXT, threshold=40) is True


def test_exact_threshold_pages():
    text = "x\n" * 40
    assert should_page(text, threshold=40) is True


def test_one_below_threshold_no_page():
    text = "x\n" * 39
    assert should_page(text, threshold=40) is False


# ---------------------------------------------------------------------------
# page_output – short text printed directly
# ---------------------------------------------------------------------------

def test_short_text_printed(capsys):
    page_output(SHORT_TEXT, threshold=40)
    captured = capsys.readouterr()
    assert captured.out.strip() == SHORT_TEXT.strip()


# ---------------------------------------------------------------------------
# page_output – long text routed through pydoc.pager by default
# ---------------------------------------------------------------------------

def test_long_text_uses_pydoc_pager(monkeypatch):
    monkeypatch.delenv("STACKDIFF_PAGER", raising=False)
    monkeypatch.delenv("PAGER", raising=False)
    with patch("stackdiff.pager.pydoc.pager") as mock_pager:
        page_output(LONG_TEXT, threshold=40)
        mock_pager.assert_called_once_with(LONG_TEXT)


def test_force_flag_pages_short_text(monkeypatch):
    monkeypatch.delenv("STACKDIFF_PAGER", raising=False)
    monkeypatch.delenv("PAGER", raising=False)
    with patch("stackdiff.pager.pydoc.pager") as mock_pager:
        page_output(SHORT_TEXT, force=True)
        mock_pager.assert_called_once()


# ---------------------------------------------------------------------------
# page_output – custom pager via environment variable
# ---------------------------------------------------------------------------

def test_custom_pager_env_var(monkeypatch):
    monkeypatch.setenv("STACKDIFF_PAGER", "less -R")
    mock_proc = MagicMock()
    mock_proc.communicate.return_value = (b"", b"")
    with patch("stackdiff.pager.subprocess.Popen", return_value=mock_proc) as mock_popen:
        page_output(LONG_TEXT, threshold=40)
        mock_popen.assert_called_once_with("less -R", shell=True, stdin=-1)


def test_fallback_pager_env_var(monkeypatch):
    monkeypatch.delenv("STACKDIFF_PAGER", raising=False)
    monkeypatch.setenv("PAGER", "more")
    mock_proc = MagicMock()
    mock_proc.communicate.return_value = (b"", b"")
    with patch("stackdiff.pager.subprocess.Popen", return_value=mock_proc) as mock_popen:
        page_output(LONG_TEXT, threshold=40)
        mock_popen.assert_called_once_with("more", shell=True, stdin=-1)
