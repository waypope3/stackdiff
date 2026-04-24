"""differ_aliaser.py – attach human-readable aliases to diff keys.

Some infrastructure stacks use opaque or auto-generated output keys
(e.g. ``Fn::Sub`` slugs, CloudFormation logical IDs).  This module lets
callers supply an *alias map* – a plain ``dict[str, str]`` that maps raw
keys to friendlier display names – and produces ``AliasedDiff`` objects
that carry both the original key and its alias.

Typical usage::

    aliases = {"VpcId": "Primary VPC", "SgId": "App Security Group"}
    aliased = alias_diffs(diffs, aliases)
    for ad in aliased:
        print(ad.alias, ad.baseline_value, ad.target_value)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from stackdiff.differ import KeyDiff

# Sentinel used when a key has no entry in the alias map.
_NO_ALIAS = ""


@dataclass(frozen=True)
class AliasedDiff:
    """A *KeyDiff* decorated with an optional human-readable alias."""

    key: str
    alias: str  # empty string when no alias was supplied
    baseline_value: Any
    target_value: Any
    changed: bool

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @property
    def display_key(self) -> str:
        """Return the alias when available, otherwise the raw key."""
        return self.alias if self.alias else self.key

    def as_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dictionary (useful for JSON export)."""
        return {
            "key": self.key,
            "alias": self.alias,
            "display_key": self.display_key,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "changed": self.changed,
        }

    def __str__(self) -> str:  # pragma: no cover
        label = self.display_key
        if self.changed:
            return f"{label}: {self.baseline_value!r} → {self.target_value!r}"
        return f"{label}: {self.baseline_value!r} (unchanged)"


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def alias_diffs(
    diffs: Sequence[KeyDiff],
    aliases: Optional[Dict[str, str]] = None,
) -> List[AliasedDiff]:
    """Attach aliases from *aliases* to each entry in *diffs*.

    Parameters
    ----------
    diffs:
        Sequence of :class:`~stackdiff.differ.KeyDiff` objects as produced
        by :func:`~stackdiff.differ.diff_stacks`.
    aliases:
        Mapping of raw key → display name.  Keys absent from the map
        receive an empty alias (``""``).  ``None`` is treated the same as
        an empty mapping.

    Returns
    -------
    list[AliasedDiff]
        One :class:`AliasedDiff` per input entry, in the same order.
    """
    if aliases is None:
        aliases = {}

    result: List[AliasedDiff] = []
    for diff in diffs:
        alias = aliases.get(diff.key, _NO_ALIAS)
        changed = diff.baseline_value != diff.target_value
        result.append(
            AliasedDiff(
                key=diff.key,
                alias=alias,
                baseline_value=diff.baseline_value,
                target_value=diff.target_value,
                changed=changed,
            )
        )
    return result


def build_alias_map(pairs: Sequence[tuple[str, str]]) -> Dict[str, str]:
    """Convenience helper – construct an alias map from a list of ``(key, alias)`` tuples.

    Duplicate keys are silently overwritten (last writer wins).

    >>> build_alias_map([("VpcId", "Primary VPC"), ("SgId", "App SG")])
    {'VpcId': 'Primary VPC', 'SgId': 'App SG'}
    """
    return dict(pairs)
