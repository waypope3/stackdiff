"""CLI entry-point for watch mode."""
from __future__ import annotations

import argparse
import sys
from typing import List

from stackdiff.differ import KeyDiff
from stackdiff.differ_watch import WatchOptions, watch
from stackdiff.formatter import format_diff


def _on_change(diffs: List[KeyDiff], colour: bool) -> None:
    print("[stackdiff] CHANGE DETECTED", flush=True)
    for line in format_diff(diffs, colour=colour):
        print(line, flush=True)


def _on_no_change() -> None:
    print("[stackdiff] no diff", flush=True)


def build_watch_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Watch two stack sources and report when diffs change."
    )
    if parent is not None:
        parser = parent.add_parser("watch", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="stackdiff-watch", **kwargs)

    parser.add_argument("baseline", help="Baseline stack file or s3:// URI")
    parser.add_argument("target", help="Target stack file or s3:// URI")
    parser.add_argument(
        "--interval", type=int, default=30, metavar="SECONDS",
        help="Polling interval in seconds (default: 30)",
    )
    parser.add_argument(
        "--no-colour", action="store_true", help="Disable colour output"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_watch_parser()
    args = parser.parse_args(argv)
    colour = not args.no_colour

    opts = WatchOptions(
        baseline_uri=args.baseline,
        target_uri=args.target,
        interval=args.interval,
        on_change=lambda diffs: _on_change(diffs, colour=colour),
        on_no_change=_on_no_change,
    )

    try:
        watch(opts)
    except KeyboardInterrupt:
        print("\n[stackdiff] watch stopped.", file=sys.stderr)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
