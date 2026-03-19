import contextlib
import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import tomlkit

if TYPE_CHECKING:
    from pathlib import Path

    from .json_object import JSONObject

logger = logging.getLogger(__name__)


@dataclass
class Config:
    layers: list[str] | None = None
    std: str | None = None
    bitmap_resolution: int | None = 2
    frame_rate: int | None = None
    max_clones: float | None = None
    no_miscellaneous_limits: bool | None = None
    no_sprite_fencing: bool | None = None
    frame_interpolation: bool | None = None
    high_quality_pen: bool | None = None
    stage_width: int | None = None
    stage_height: int | None = None


def find_turbowarp_config_comment(project: JSONObject) -> str | None:
    stage = next(target for target in project.targets if target.isStage)
    for comment in stage.comments._.values():
        if comment.text.endswith("_twconfig_"):
            return comment.text
    return None


def parse_turbowarp_config_comment(text: str | None) -> dict[str, Any] | None:
    if text and (start := text.find("{")) != -1 and (end := text.rfind("}")) != -1:
        with contextlib.suppress(json.JSONDecodeError):
            return json.loads(text[start : end + 1])
    return None


def get_layers(project: JSONObject) -> list[str]:
    layers = sorted(project.targets, key=lambda target: target.layerOrder)
    return [layer.name for layer in layers if layer.name != "Stage"]


def decompile_config(project: JSONObject) -> Config:
    config = Config()
    data = parse_turbowarp_config_comment(find_turbowarp_config_comment(project)) or {}
    runtime_options = data.get("runtimeOptions", {})
    config.layers = get_layers(project)
    config.frame_rate = data.get("framerate")
    config.max_clones = runtime_options.get("maxClones")
    config.no_miscellaneous_limits = runtime_options.get("miscLimits") is False
    config.no_sprite_fencing = runtime_options.get("fencing") is False
    config.frame_interpolation = data.get("interpolation") is True
    config.high_quality_pen = data.get("hq") is True
    config.stage_width = data.get("width")
    config.stage_height = data.get("height")
    return config


def write_config(config: Config, output: Path) -> None:
    doc = tomlkit.document()
    for key, value in config.__dict__.items():
        if value is not None:
            doc.add(key, value)
    with output.joinpath("goboscript.toml").open("w") as file:
        tomlkit.dump(doc, file)
