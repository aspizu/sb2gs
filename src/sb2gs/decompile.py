import itertools
import json
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile

from . import costumes
from .decompile_config import decompile_config, write_config
from .decompile_sprite import Ctx, decompile_sprite
from .json_object import JSONObject


def get_asset_filename(name: str, md5ext: str) -> str:
    name = "forward-slash" if name == "/" else name.replace("/", "")
    if sys.platform == "win32" or name == "":
        name = md5ext[:8]
    return name + Path(md5ext).suffix


def get_asset_names(project: JSONObject, key: str) -> dict[str, str]:
    assets: dict[str, str] = {}
    filenames: dict[str, str] = {}
    for asset in itertools.chain(*(target._[key] for target in project.targets)):
        if asset.md5ext in assets:
            continue
        i = 2
        filename = get_asset_filename(asset.name, asset.md5ext)
        while filename in filenames:
            filename = get_asset_filename(f"{asset.name} ({i})", asset.md5ext)
            i += 1
        assets[asset.md5ext] = filename
        filenames[filename] = asset.md5ext
    return assets


def sanitize_sprite_name(name: str) -> str:
    return name.replace("/", "_")


def rename_sprites(project: JSONObject, name_map: dict[str, str]) -> None:
    """Update sprite names and block field references to renamed sprites in-place."""
    for target in project.targets:
        if target.name in name_map:
            target._["name"] = name_map[target.name]
        for block in target.blocks._.values():
            if not isinstance(block, JSONObject):
                continue
            for field_values in block.fields._.values():
                if isinstance(field_values, list) and field_values and field_values[0] in name_map:
                    field_values[0] = name_map[field_values[0]]


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
    name_map = {t.name: sanitize_sprite_name(t.name) for t in sprites if "/" in t.name}
    if name_map:
        rename_sprites(project, name_map)
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
