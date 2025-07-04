from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from pathlib import Path

    from .json_object import JSONObject

logger = logging.getLogger(__name__)

svg = "{http://www.w3.org/2000/svg}"
ET.register_namespace("", "http://www.w3.org/2000/svg")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")


def fix_vector_center(costume: JSONObject, path: Path) -> None:
    et = ET.parse(path)
    root = et.getroot()
    if (
        float(root.attrib.get("width", "0")) / 2 == costume.rotationCenterX
        and float(root.attrib.get("height", "0")) / 2 == costume.rotationCenterY
    ):
        return
    root.set("width", "480")
    root.set("height", "360")
    root.set("viewBox", "0,0,480,360")
    group = root.find(f"{svg}g")
    if group is None:
        return
    group.attrib.pop("transform", None)
    with path.open("wb") as file:
        et.write(file, encoding="utf-8", xml_declaration=False)


def fix_bitmap_center(costume: JSONObject, path: Path) -> None:
    img = Image.open(path)
    if (
        costume.rotationCenterX == img.width // 2
        and costume.rotationCenterY == img.height // 2
    ):
        return
    fixed = Image.new("RGBA", (960, 720), (0, 0, 0, 0))
    fixed.paste(img, (480 - costume.rotationCenterX, 360 - costume.rotationCenterY))
    fixed.save(path, format=costume.dataFormat)


def fix_center(costume: JSONObject, path: Path, fixed: set[str]) -> None:
    if costume.md5ext in fixed:
        return
    fixed.add(costume.md5ext)
    if costume.dataFormat == "svg":
        fix_vector_center(costume, path)
    else:
        fix_bitmap_center(costume, path)
