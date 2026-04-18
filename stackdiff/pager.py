"""Optional paged output for long diffs."""
from __future__ import annotations

import os
import pydoc
import shutil
from typing import Optional


_PAGER_ENV_VAR = "STACKDIFF_PAGER"
_DEFAULT_THRESHOLD = 40  # lines


def _terminal_height() -> int:
    """Return the current terminal height, falling back to a safe default."""
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.lines


def should_page(text: str, threshold: Optional[int] = None) -> bool:
    """Return True when *text* is long enough to warrant paging.

    The threshold defaults to the terminal height minus two header lines,
    but can be overridden explicitly (useful in tests).
    """
    if threshold is None:
        threshold = max(_DEFAULT_THRESHOLD, _terminal_height() - 2)
    return text.count("\n") >= threshold


def page_output(text: str, force: bool = False, threshold: Optional[int] = None) -> None:
    """Print *text*, routing through a pager when the output is long.

    The pager command is taken from the ``STACKDIFF_PAGER`` environment
    variable, then ``PAGER``, then falls back to :func:`pydoc.pager`.

    Args:
        text:      The string to display.
        force:     Always page, regardless of length.
        threshold: Line count at which paging kicks in (default: terminal height).
    """
    use_pager = force or should_page(text, threshold=threshold)

    if not use_pager:
        print(text)
        return

    custom = os.environ.get(_PAGER_ENV_VAR) or os.environ.get("PAGER")
    if custom:
        import subprocess
        proc = subprocess.Popen(custom, shell=True, stdin=subprocess.PIPE)
        try:
            proc.communicate(input=text.encode())
        except BrokenPipeError:
            pass
    else:
        pydoc.pager(text)
