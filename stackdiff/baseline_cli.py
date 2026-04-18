"""CLI sub-commands for baseline management."""
from __future__ import annotations

import argparse
import sys

from stackdiff.baseline import compare_to_baseline, update_baseline, BaselineError
from stackdiff.parser import load_stack
from stackdiff.reporter import generate_report
from stackdiff.snapshot import list_snapshots


def _cmd_compare(args: argparse.Namespace) -> int:
    try:
        stack = load_stack(args.stack_file)
        result = compare_to_baseline(stack, args.name, snap_dir=args.snap_dir)
    except BaselineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = generate_report(result.diffs, fmt=args.format)
    print(report)
    return 1 if result.summary.has_diff() else 0


def _cmd_update(args: argparse.Namespace) -> int:
    try:
        stack = load_stack(args.stack_file)
        path = update_baseline(stack, args.name, snap_dir=args.snap_dir)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Baseline '{args.name}' saved to {path}")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    names = list_snapshots(snap_dir=args.snap_dir)
    if not names:
        print("No baselines found.")
    for name in names:
        print(name)
    return 0


def build_baseline_parser(parent: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--snap-dir", default=".stackdiff/snapshots")

    p_cmp = parent.add_parser("baseline-compare", parents=[common])
    p_cmp.add_argument("stack_file")
    p_cmp.add_argument("name")
    p_cmp.add_argument("--format", default="text", choices=["text", "json", "markdown"])
    p_cmp.set_defaults(func=_cmd_compare)

    p_upd = parent.add_parser("baseline-update", parents=[common])
    p_upd.add_argument("stack_file")
    p_upd.add_argument("name")
    p_upd.set_defaults(func=_cmd_update)

    p_lst = parent.add_parser("baseline-list", parents=[common])
    p_lst.set_defaults(func=_cmd_list)
