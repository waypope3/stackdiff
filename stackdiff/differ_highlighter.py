"""Inline character-level diff highlighting for changed values."""
from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from typing import List

from stackdiff.differ import KeyDiff

_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_BOLD = "\033[1m"


@dataclass
class HighlightedDiff:
    key: str
    baseline_highlighted: str
    target_highlighted: str
    changed: bool
    opcodes: List[tuple] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_highlighted": self.baseline_highlighted,
            "target_highlighted": self.target_highlighted,
            "changed": self.changed,
        }


def _apply_opcodes(
    a: str,
    b: str,
    opcodes: list,
    colour_remove: str,
    colour_insert: str,
) -> tuple[str, str]:
    """Return (a_highlighted, b_highlighted) with inline ANSI colour spans."""
    a_out: List[str] = []
    b_out: List[str] = []
    for tag, i1, i2, j1, j2 in opcodes:
        a_chunk = a[i1:i2]
        b_chunk = b[j1:j2]
        if tag == "equal":
            a_out.append(a_chunk)
            b_out.append(b_chunk)
        elif tag == "replace":
            a_out.append(f"{colour_remove}{_BOLD}{a_chunk}{_RESET}")
            b_out.append(f"{colour_insert}{_BOLD}{b_chunk}{_RESET}")
        elif tag == "delete":
            a_out.append(f"{colour_remove}{_BOLD}{a_chunk}{_RESET}")
        elif tag == "insert":
            b_out.append(f"{colour_insert}{_BOLD}{b_chunk}{_RESET}")
    return "".join(a_out), "".join(b_out)


def highlight_diffs(
    diffs: List[KeyDiff],
    colour: bool = True,
) -> List[HighlightedDiff]:
    """Produce character-level highlighted diffs for a list of KeyDiff objects."""
    results: List[HighlightedDiff] = []
    for d in diffs:
        a = str(d.baseline_value) if d.baseline_value is not None else ""
        b = str(d.target_value) if d.target_value is not None else ""
        changed = a != b
        if changed and colour:
            matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
            opcodes = matcher.get_opcodes()
            a_hl, b_hl = _apply_opcodes(a, b, opcodes, _RED, _GREEN)
        else:
            a_hl, b_hl = a, b
            opcodes = []
        results.append(
            HighlightedDiff(
                key=d.key,
                baseline_highlighted=a_hl,
                target_highlighted=b_hl,
                changed=changed,
                opcodes=opcodes,
            )
        )
    return results
