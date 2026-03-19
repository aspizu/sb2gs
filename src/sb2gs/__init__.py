import functools
import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from time import perf_counter_ns
from typing import TYPE_CHECKING

from rich import print

from ._logging import setup_logging
from .decompile import decompile
from .sb3_downloader import download_sb3
from .verify import verify

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)


def entrypoint(func: Callable[[], None]) -> Callable[[], int]:
    @functools.wraps(func)
    def wrapper() -> int:
        before = perf_counter_ns()
        success = True
        func()
        after = perf_counter_ns()
        color = "[green]" if success else "[red]"
        print(f"[dim][bold]{color}Finished[/] in {(after - before) / 1e6}ms")
        if not success:
            return 1
        return 0

    return wrapper


def determine_output_path(input: Path, output: Path | None, overwrite: bool) -> Path:
    output = output or input.parent.joinpath(input.stem)
    if output.exists() and not overwrite:
        logger.error("output directory already exists. (use --overwrite to overwrite)")
        sys.exit(1)
    return output


@entrypoint
def main() -> None:
    setup_logging()
    argparser = ArgumentParser("sb2gs")
    argparser.add_argument("input", type=Path)
    argparser.add_argument("output", nargs="?", type=Path)
    argparser.add_argument("--overwrite", action="store_true")
    argparser.add_argument("--id", type=str, help="Download the project with this ID.")
    argparser.add_argument(
        "--verify",
        action="store_true",
        help="Invoke goboscript to verify that the decompiled code is valid. This does "
        "not indicate that the decompiled code is equivalent to the original.",
    )
    args = argparser.parse_args()
    if args.input.suffix != ".sb3":
        logger.error("input must be a `.sb3` file.")
        sys.exit(1)
    args.output = determine_output_path(args.input, args.output, args.overwrite)
    if args.id and not args.input.exists():
        download_sb3(args.id, args.input)
    decompile(args.input, args.output)
    if args.verify:
        verify(args.output)
