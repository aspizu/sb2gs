from __future__ import annotations

from typing import TYPE_CHECKING

from .decompile_code import decompile_value
from .decompile_events import decompile_events
from .string_builder import StringBuilder
from .syntax import create_identifier, create_number, create_string

if TYPE_CHECKING:
    from .json_object import JSONObject
    from .types import Block


class Ctx(StringBuilder):
    def __init__(self, target: JSONObject, indent_width: int = 4) -> None:
        super().__init__(indent_width)
        self.is_stage: bool = target.isStage
        self.costumes: list[JSONObject] = target.costumes
        self.sounds: list[JSONObject] = target.sounds
        self.variables: JSONObject = target.variables
        self.lists: JSONObject = target.lists
        self.blocks: dict[str, Block] = target.blocks._
        self.volume: float = target.volume
        self.layer_order: int = target.layerOrder
        if not self.is_stage:
            self.visible: bool = target.visible
            self.x: float = target.x
            self.y: float = target.y
            self.size: float = target.size
            self.direction: float = target.direction
            self.draggable: bool = target.draggable
            self.rotation_style: str = target.rotationStyle


def decompile_asset(ctx: Ctx, asset: JSONObject) -> None:
    ctx.print(
        create_string("assets/" + asset.md5ext),
        " as ",
        create_string(asset.name),
    )


def decompile_common_properties(ctx: Ctx) -> None:
    ctx.iprintln("layer_order ", create_number(ctx.layer_order), ";")
    if ctx.volume != DEFAULT_VOLUME:
        ctx.iprintln("set_volume ", create_number(ctx.volume), ";")


DEFAULT_VOLUME = 100
DEFAULT_X = 0
DEFAULT_Y = 0
DEFAULT_SIZE = 100
DEFAULT_DIRECTION = 90


def decompile_sprite_properties(ctx: Ctx) -> None:
    if not ctx.visible:
        ctx.iprintln("hide;")
    if ctx.x != DEFAULT_X:
        ctx.iprintln("set_x ", create_number(ctx.x), ";")
    if ctx.y != DEFAULT_Y:
        ctx.iprintln("set_y ", create_number(ctx.y), ";")
    if ctx.size != DEFAULT_SIZE:
        ctx.iprintln("set_size ", create_number(ctx.size), ";")
    if ctx.direction != DEFAULT_DIRECTION:
        ctx.iprintln("point_in_direction ", create_number(ctx.direction), ";")
    decompile_rotation_style(ctx)
    if ctx.draggable:
        ctx.iprintln("set_draggable;")


def decompile_rotation_style(ctx: Ctx) -> None:
    if ctx.rotation_style == "left-right":
        ctx.iprintln("set_rotation_style_left_right;")
    if ctx.rotation_style == "don't rotate":
        ctx.iprintln("set_rotation_style_do_not_rotate;")


def decompile_properties(ctx: Ctx) -> None:
    decompile_common_properties(ctx)
    if not ctx.is_stage:
        decompile_sprite_properties(ctx)


def decompile_costumes(ctx: Ctx) -> None:
    if not ctx.costumes:
        return
    ctx.iprint("costumes ")
    ctx.commasep(ctx.costumes, decompile_asset, pass_self=True)
    ctx.println(";")


def decompile_sounds(ctx: Ctx) -> None:
    if not ctx.sounds:
        return
    ctx.iprint("sounds ")
    ctx.commasep(ctx.sounds, decompile_asset, pass_self=True)
    ctx.println(";")


def decompile_variables(ctx: Ctx) -> None:
    for variable_name, variable_value in ctx.variables._.values():
        ctx.iprint("var ", create_identifier(variable_name), " = ")
        decompile_value(ctx, variable_value)
        ctx.println(";")


def decompile_lists(ctx: Ctx) -> None:
    for list_name, list_values in ctx.lists._.values():
        ctx.iprint("list ", create_identifier(list_name))
        if not list_values:
            ctx.println(";")
            continue
        ctx.print(" = [")
        ctx.commasep(list_values, decompile_value, pass_self=True)
        ctx.println("];")


def decompile_sprite(ctx: Ctx) -> None:
    decompile_properties(ctx)
    decompile_costumes(ctx)
    decompile_sounds(ctx)
    decompile_variables(ctx)
    decompile_lists(ctx)
    decompile_events(ctx)
