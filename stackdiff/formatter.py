"""Render a DiffResult as coloured terminal output or plain text."""

from typing import TextIO
import sys

from stackdiff.differ import DiffResult

ANSI_GREEN = "\033[32m"
ANSI_RED = "\033[31m"
ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"


def _colour(text: str, code: str, use_colour: bool) -> str:
    if use_colour:
        return f"{code}{text}{ANSI_RESET}"
    return text


def format_diff(
    result: DiffResult,
    out: TextIO = sys.stdout,
    use_colour: bool = True,
) -> None:
    """Write a human-readable diff to *out*."""
    for key, value in sorted(result.added.items()):
        line = f"+ {key} = {value}"
        out.write(_colour(line, ANSI_GREEN, use_colour) + "\n")

    for key, value in sorted(result.removed.items()):
        line = f"- {key} = {value}"
        out.write(_colour(line, ANSI_RED, use_colour) + "\n")

    for key, (old, new) in sorted(result.changed.items()):
        old_line = f"- {key} = {old}"
        new_line = f"+ {key} = {new}"
        out.write(_colour(old_line, ANSI_RED, use_colour) + "\n")
        out.write(_colour(new_line, ANSI_GREEN, use_colour) + "\n")

    out.write(_colour(result.summary(), ANSI_YELLOW, use_colour) + "\n")
