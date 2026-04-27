"""Streak detection: identify keys whose values have changed consistently
across a sequence of diff results (e.g. always increasing, always changing)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from stackdiff.differ import KeyDiff


@dataclass
class StreakedDiff:
    key: str
    baseline_value: str
    target_value: str
    changed: bool
    streak: int  # consecutive diffs where this key was changed
    always_changed: bool  # True if changed in every supplied diff result

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
            "streak": self.streak,
            "always_changed": self.always_changed,
        }

    def __str__(self) -> str:  # pragma: no cover
        marker = "~" if self.changed else "="
        streak_note = f" [streak={self.streak}]" if self.streak > 1 else ""
        return f"{marker} {self.key}: {self.baseline_value!r} -> {self.target_value!r}{streak_note}"


def streak_diffs(
    current: Sequence[KeyDiff],
    history: Sequence[Sequence[KeyDiff]],
) -> List[StreakedDiff]:
    """Compute streaks for *current* diffs given zero or more prior diff rounds.

    Parameters
    ----------
    current:
        The most-recent list of KeyDiff objects (the diff being annotated).
    history:
        Older diff rounds ordered oldest-first.  Each element is a sequence
        of KeyDiff objects from a previous comparison.
    """
    # Build a lookup of {key: was_changed} for every historical round
    history_maps: List[dict] = [
        {d.key: d.baseline_value != d.target_value for d in round_}
        for round_ in history
    ]

    results: List[StreakedDiff] = []
    for diff in current:
        changed_now = diff.baseline_value != diff.target_value

        # Count consecutive rounds (going backwards) where this key changed
        streak = 1 if changed_now else 0
        if changed_now:
            for past in reversed(history_maps):
                if past.get(diff.key, False):
                    streak += 1
                else:
                    break

        total_rounds = len(history_maps) + 1  # including current
        always = changed_now and streak == total_rounds

        results.append(
            StreakedDiff(
                key=diff.key,
                baseline_value=diff.baseline_value,
                target_value=diff.target_value,
                changed=changed_now,
                streak=streak,
                always_changed=always,
            )
        )
    return results
