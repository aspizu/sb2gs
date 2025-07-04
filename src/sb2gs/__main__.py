from __future__ import annotations

import sys
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path
from sys import stderr
from time import perf_counter_ns

from rich import print

from ._logging import setup_logging
from .decompile import decompile
from .errors import Error
from .verify import verify


def input_type(value: str) -> Path:
    path = Path(value)
    if path.suffix != ".sb3":
        msg = "must have file extension .sb3"
        raise ArgumentTypeError(msg)
    if not path.exists():
        msg = "file does not exist"
        raise ArgumentTypeError(msg)
    if not path.is_file():
        msg = "is not a file"
        raise ArgumentTypeError(msg)
    return path


def output_type(value: str) -> Path:
    path = Path(value)
    if path.is_file():
        msg = "exists, and is a file"
        raise ArgumentTypeError(msg)
    return path


def determine_output_path(input: Path, output: Path | None, overwrite: bool) -> Path:
    output = output or input.parent.joinpath(input.stem)
    if output.exists() and not overwrite:
        msg = "output directory already exists. (use --overwrite to overwrite)"
        raise Error(msg)
    return output


def main() -> None:
    setup_logging()
    argparser = ArgumentParser()
    argparser.add_argument("input", type=input_type)
    argparser.add_argument("output", nargs="?", type=output_type)
    argparser.add_argument("--overwrite", action="store_true")
    argparser.add_argument(
        "--verify",
        action="store_true",
        help="Invoke goboscript to verify that the decompiled code is valid. This does "
        "not indicate that the decompiled code is equivalent to the original.",
    )
    args = argparser.parse_args()
    args.output = determine_output_path(args.input, args.output, args.overwrite)
    decompile(args.input, args.output)
    if args.verify:
        verify(args.output)


before = perf_counter_ns()
success = True
try:
    main()
except Error as error:
    stderr.write(f"error: {error}\n")
    stderr.flush()
    success = False
after = perf_counter_ns()
color = "[green]" if success else "[red]"
print(f"[dim][bold]{color}Finished[/] in {(after - before) / 1e6}ms")
if not success:
    sys.exit(1)
