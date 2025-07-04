from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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

    def to_json(self) -> dict[str, object]:
        return self.__dict__


def get_config(project: JSONObject) -> Config:
    stage = next(target for target in project.targets if target.isStage)
    comment: str | None = next(
        (
            comment.text
            for comment in stage.comments._.values()
            if comment.text.endswith("// _twconfig_")
        ),
        None,
    )
    if comment is None:
        return Config()
    data = json.loads(comment[comment.find("{") : comment.rfind("}") + 1])
    runtime_options = data.get("runtimeOptions", {})
    config = Config()
    config.frame_rate = data.get("framerate")
    config.max_clones = runtime_options.get("maxClones")
    config.no_miscellaneous_limits = runtime_options.get("miscLimits") is False
    config.no_sprite_fencing = runtime_options.get("fencing") is False
    config.frame_interpolation = data.get("interpolation") is True
    config.high_quality_pen = data.get("hq") is True
    config.stage_width = data.get("width")
    config.stage_height = data.get("height")
    return config
