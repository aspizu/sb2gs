from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import toml

if TYPE_CHECKING:
    from pathlib import Path

    from .json_object import JSONObject

logger = logging.getLogger(__name__)


@dataclass
class Config:
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
    if text is None:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def decompile_config(project: JSONObject, output: Path) -> None:
    config = Config()
    data = parse_turbowarp_config_comment(find_turbowarp_config_comment(project)) or {}
    runtime_options = data.get("runtimeOptions", {})
    config.frame_rate = data.get("framerate")
    config.max_clones = runtime_options.get("maxClones")
    config.no_miscellaneous_limits = runtime_options.get("miscLimits") is False
    config.no_sprite_fencing = runtime_options.get("fencing") is False
    config.frame_interpolation = data.get("interpolation") is True
    config.high_quality_pen = data.get("hq") is True
    config.stage_width = data.get("width")
    config.stage_height = data.get("height")
    with output.joinpath("goboscript.toml").open("w") as file:
        toml.dump(config.__dict__, file)
