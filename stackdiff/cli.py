"""Command-line interface for stackdiff."""

import sys
import argparse

from stackdiff.parser import load_stack, StackParseError
from stackdiff.differ import diff_stacks
from stackdiff.formatter import format_diff


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff",
        description="Compare infrastructure stack outputs across environments.",
    )
    parser.add_argument(
        "baseline",
        metavar="BASELINE",
        help="Path to the baseline stack file (JSON or YAML).",
    )
    parser.add_argument(
        "target",
        metavar="TARGET",
        help="Path to the target stack file to compare against baseline.",
    )
    parser.add_argument(
        "--no-colour",
        action="store_true",
        default=False,
        help="Disable coloured output.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences are found.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        baseline = load_stack(args.baseline)
        target = load_stack(args.target)
    except StackParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = diff_stacks(baseline, target)
    output = format_diff(result, colour=not args.no_colour)

    if output:
        print(output)

    if args.exit_code and result.has_diff:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
