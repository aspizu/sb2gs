import json
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile

from . import costumes
from .decompile_config import decompile_config, write_config
from .decompile_sprite import Ctx, decompile_sprite
from .json_object import JSONObject


def get_asset_names(project: JSONObject, key: str) -> dict[str, str]:
    assets: dict[str, str] = {}
    for asset in (asset for target in project.targets for asset in target._[key]):
        name = asset.name.replace("/", "") + Path(asset.md5ext).suffix
        if sys.platform == "win32" or assets.get(name, asset.md5ext) != asset.md5ext:
            name = asset.md5ext
        assets[asset.md5ext] = name
    return assets


def decompile(input: Path, output: Path) -> None:
    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True, exist_ok=True)
    assets_path = output.joinpath("assets")
    assets_path.mkdir()
    with ZipFile(input) as zf, zf.open("project.json") as f:
        project = json.load(f, object_hook=JSONObject)
        assets = get_asset_names(project, "costumes")
        assets.update(get_asset_names(project, "sounds"))
        for md5ext, name in assets.items():
            with zf.open(md5ext) as src, assets_path.joinpath(name).open("wb") as dest:
                shutil.copyfileobj(src, dest)
    stage = next(target for target in project.targets if target.isStage)
    sprites = [target for target in project.targets if not target.isStage]
    ctx = Ctx(stage, assets)
    with output.joinpath("stage.gs").open("w") as file:
        decompile_sprite(ctx)
        file.write(str(ctx))
    fixed = set()
    for target in sprites:
        ctx = Ctx(target, assets)
        for costume in target.costumes:
            costumes.fix_center(
                costume,
                assets_path.joinpath(assets[costume.md5ext]),
                fixed,
            )
        with output.joinpath(f"{target.name}.gs").open("w") as file:
            decompile_sprite(ctx)
            file.write(str(ctx))
    write_config(decompile_config(project), output)
