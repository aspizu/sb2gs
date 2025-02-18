from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from zipfile import ZipFile

from .decompiler import Blocks
from .sb3 import Namespace, Project

EXT = "gs"


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

    if path.is_dir() and not (path / f"stage.{EXT}").is_file() and any(path.iterdir()):
        raise argparse.ArgumentTypeError(f"{arg} exists and is not empty.")
    return path


argparser = argparse.ArgumentParser(
    prog="sb2gs",
    description="The goboscript decompiler.",
    epilog="homepage: https://github.com/aspizu/sb2gs",
)

argparser.add_argument(
    "-i", "--input", type=parsearg_input, help="Scratch project file.", required=True
)
argparser.add_argument("-o", "--output", type=parsearg_output, help="Output directory.")
argparser.add_argument(
    "-f", "--force", action="store_true", help="Overwrite existing files."
)

args = argparser.parse_args()
input: Path = args.input
output: Path = args.output or args.input.parent.joinpath(args.input.stem)
force = args.force
if force:
    shutil.rmtree(output, ignore_errors=True)
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
        costumefile = output / target.name / costume.md5ext
        prettycostumepath = (
            output / target.name / f"{costume.name}.{costume.dataFormat}"
        )
        if prettycostumepath.exists():
            costumefile.unlink()
        else:
            costumefile.rename(prettycostumepath)
    with (output / f"{target.name}.{EXT}").open("w") as file:
        blocks = Blocks(target, file)
        blocks.all()
