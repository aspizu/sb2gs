import argparse
from pathlib import Path

from builder import Builder


def main() -> None:
    def input_parse(i: str) -> Path:
        o = Path(i)
        if not o.exists():
            raise argparse.ArgumentTypeError(f"{o} does not exist")
        if not o.is_file() or not o.name.endswith("sb3"):
            raise argparse.ArgumentTypeError(f"{o} is not a Scratch project")
        return o

    def output_parse(i: str) -> Path:
        o = Path(i)
        if o.is_file():
            raise argparse.ArgumentTypeError(f"{o} is a file")
        return o

    parser = argparse.ArgumentParser(
        prog="sb2gs", description="Convert a Scratch project into a GoboScript project"
    )
    parser.add_argument("-input", type=input_parse)
    parser.add_argument("-output", type=output_parse)
    args = parser.parse_args()
    input: Path = args.input
    output: Path = args.output
    Builder(input, output)


main()
