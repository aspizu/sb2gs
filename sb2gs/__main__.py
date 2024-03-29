from __future__ import annotations
import json
import argparse
from pathlib import Path
from zipfile import ZipFile
from .sb3 import Project, Namespace
from .decompiler import Blocks

EXT = "gobo"


def parsearg_input(arg: str) -> Path:
    path = Path(arg)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"{arg} does not exist.")
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"{arg} is not a file.")
    if path.suffix != ".sb3":
        raise argparse.ArgumentTypeError(f"{arg} is not a Scratch project file.")
    return path


def parsearg_output(arg: str) -> Path:
    path = Path(arg)
    if path.is_file():
        raise argparse.ArgumentTypeError(f"{arg} is a file.")

    if path.is_dir() and not (path / "stage.gobo").is_file() and any(path.iterdir()):
        raise argparse.ArgumentTypeError(f"{arg} exists and is not empty.")
    return path


argparser = argparse.ArgumentParser(
    prog="sb2gs",
    description="The goboscript decompiler.",
    epilog="homepage: https://github.com/aspizu/sb2gs",
)

argparser.add_argument(
    "-input", type=parsearg_input, help="Scratch project file.", required=True
)
argparser.add_argument(
    "-output", type=parsearg_output, help="Output directory.", required=True
)

args = argparser.parse_args()
input: Path = args.input
output: Path = args.output
output.mkdir(exist_ok=True)

zf = ZipFile(input)
project: Project = json.load(zf.open("project.json"), object_hook=Namespace)
if project.meta.semver != "3.0.0":
    msg = f"Unsupported Scratch version {project.meta.semver}"
    raise RuntimeError(msg)

for target in project.targets:
    if "/" in target.name:
        msg = f"Sprite \"{target.name}\" name contains '/', rename required."
        raise RuntimeError(msg)
    if target.name == "stage":
        msg = 'Sprite is named "stage", rename required.'
        raise RuntimeError(msg)
    if target.name == "Stage":
        target.name = "stage"
    (output / target.name).mkdir(exist_ok=True)
    for costume in target.costumes:
        costume.name = costume.name.replace("/", "{{fwslash}}")
        zf.extract(costume.md5ext, output / target.name)
        (output / target.name / costume.md5ext).rename(
            output / target.name / f"{costume.name}.{costume.dataFormat}"
        )
    with (output / f"{target.name}.{EXT}").open("w") as file:
        blocks = Blocks(target, file)
        blocks.all()
