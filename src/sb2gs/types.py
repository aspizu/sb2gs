from __future__ import annotations

from dataclasses import dataclass

from .json_object import JSONObject


@dataclass
class Block(JSONObject):
    opcode: str
    next: str | None
    parent: str | None
    inputs: JSONObject
    field: JSONObject
    shadow: bool
    topLevel: bool
    x: int
    y: int
