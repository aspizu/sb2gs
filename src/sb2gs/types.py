from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .json_object import JSONObject


class InputType(IntEnum):
    MATH_NUM = 4
    POSITIVE_NUM = 5
    WHOLE_NUM = 6
    INTEGER_NUM = 7
    ANGLE_NUM = 8
    COLOR_PICKER = 9
    TEXT = 10
    BROADCAST = 11
    VAR = 12
    LIST = 13


@dataclass
class Block(JSONObject):
    opcode: str
    next: str | None
    parent: str | None
    inputs: JSONObject
    fields: JSONObject[tuple[str, str | None]]
    shadow: bool
    topLevel: bool
    x: int
    y: int
