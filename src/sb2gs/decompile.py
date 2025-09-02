from __future__ import annotations

import json
import logging
import shutil
from typing import TYPE_CHECKING
from zipfile import ZipFile

from sb2gs.decompile_config import decompile_config

from . import costumes
from .decompile_sprite import Ctx, decompile_sprite
from .errors import Error
from .json_object import JSONObject

if TYPE_CHECKING:
    from pathlib import Path


def decompile(input: Path, output: Path) -> None:
    assets_path = output.joinpath("assets")
    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True, exist_ok=True)
    with ZipFile(input) as zf, zf.open("project.json") as f:
        project = json.load(f, object_hook=JSONObject)
        for file in zf.filelist:
            if file.filename != "project.json":
                zf.extract(file, assets_path)
    stage = next(target for target in project.targets if target.isStage)
    sprites = [target for target in project.targets if not target.isStage]

    ctx = Ctx(stage)
    with output.joinpath("stage.gs").open("w") as file:
        decompile_sprite(ctx)
        file.write(str(ctx))
    fixed = set()
    for target in sprites:
        ctx = Ctx(target)
        for costume in target.costumes:
            costumes.fix_center(costume, assets_path.joinpath(costume.md5ext), fixed)
        with output.joinpath(f"{target.name}.gs").open("w") as file:
            decompile_sprite(ctx)
            file.write(str(ctx))
    decompile_config(project, output)
