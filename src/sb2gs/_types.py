from __future__ import annotations

from dataclasses import dataclass, field
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
    next: str | None = None
    parent: str | None = None
    inputs: JSONObject = field(default_factory=lambda: JSONObject({}))
    fields: JSONObject[tuple[str, str | None]] = field(
        default_factory=lambda: JSONObject({})
    )
    shadow: bool = False
    topLevel: bool = False
    x: int = 0
    y: int = 0


@dataclass
class Signature:
    opcode: str
    inputs: list[str]
    menu: str | None = None
    field: str | None = None
    overloads: dict[str, str] | None = None
