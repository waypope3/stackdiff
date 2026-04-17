"""Command-line interface for stackdiff."""
from __future__ import annotations

import argparse
import sys

from stackdiff.resolver import resolve_source
from stackdiff.parser import load_stack
from stackdiff.validator import validate_stack
from stackdiff.filter import apply_filters
from stackdiff.differ import diff_stacks, has_diff
from stackdiff.sorter import SortOrder, sort_keys
from stackdiff.reporter import generate_report
from stackdiff.output import write_report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stackdiff",
        description="Compare infrastructure stack outputs across environments.",
    )
    p.add_argument("baseline", help="Baseline stack file or s3:// URI")
    p.add_argument("target", help="Target stack file or s3:// URI")
    p.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    p.add_argument("--output", metavar="FILE", help="Write report to FILE instead of stdout")
    p.add_argument("--include", metavar="PATTERN", action="append", default=[])
    p.add_argument("--exclude", metavar="PATTERN", action="append", default=[])
    p.add_argument(
        "--sort",
        choices=[o.value for o in SortOrder],
        default=SortOrder.ALPHA.value,
        help="Key sort order in the report (default: alpha)",
    )
    p.add_argument(
        "--fail-on-diff",
        action="store_true",
        help="Exit with code 1 when differences are found",
    )
    return p


def main(argv: list[str] | None = None) -> int:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args(argv)

    baseline_raw = resolve_source(args.baseline)
    target_raw = resolve_source(args.target)

    baseline_stack = load_stack(baseline_raw)
    target_stack = load_stack(target_raw)

    validate_stack(baseline_stack)
    validate_stack(target_stack)

    baseline_filtered = apply_filters(baseline_stack["Outputs"], args.include, args.exclude)
    target_filtered = apply_filters(target_stack["Outputs"], args.include, args.exclude)

    result = diff_stacks(baseline_filtered, target_filtered)

    sort_order = SortOrder(args.sort)
    result.keys_order = list(sort_keys(result.diff, sort_order).keys())

    report = generate_report(result, fmt=args.format)
    write_report(report, path=args.output)

    if args.fail_on_diff and has_diff(result):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
