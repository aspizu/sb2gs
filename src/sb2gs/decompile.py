from __future__ import annotations

import json
import shutil
from typing import TYPE_CHECKING
from zipfile import ZipFile

import toml

from . import costumes
from .config import get_config
from .decompile_sprite import Ctx, decompile_sprite
from .errors import Error
from .json_object import JSONObject

if TYPE_CHECKING:
    from pathlib import Path


def decompile(input: Path, output: Path) -> None:
    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True, exist_ok=True)
    assets_path = output.joinpath("assets")
    with ZipFile(input) as zf, zf.open("project.json") as f:
        project = json.load(f, object_hook=JSONObject)
        for file in zf.filelist:
            if file.filename == "project.json":
                continue
            zf.extract(file, assets_path)
    if project.meta.semver != "3.0.0":
        msg = f"project semver ({project.meta.semver}) is unsupported"
        raise Error(msg)
    if project.meta.vm not in {"0.2.0", "11.3.0"}:
        msg = f"project vm version ({project.meta.vm}) is unsupported"
        raise Error(msg)
    stage = next(target for target in project.targets if target.isStage)
    sprites = [target for target in project.targets if not target.isStage]
    with output.joinpath("stage.gs").open("w") as file:
        ctx = Ctx(stage)
        decompile_sprite(ctx)
        file.write(str(ctx))
    for target in sprites:
        fixed = set()
        for costume in target.costumes:
            costumes.fix_center(costume, assets_path.joinpath(costume.md5ext), fixed)
        with output.joinpath(f"{target.name}.gs").open("w") as file:
            ctx = Ctx(target)
            decompile_sprite(ctx)
            file.write(str(ctx))
    with output.joinpath("goboscript.toml").open("w") as f:
        toml.dump(get_config(project).to_json(), f)
