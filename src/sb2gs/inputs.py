from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._types import Block
    from .decompile_sprite import Ctx


def block_id(input: list[Any] | None) -> str | None:
    if input is None:
        return None
    if isinstance(input[1], str):
        return input[1]
    return None


def menu(ctx: Ctx, block: Block, menu_name: str | None) -> str | None:
    if menu_name is None:
        return None
    menu_id = block_id(block.inputs._.get(menu_name))
    if menu_id is None:
        return None
    menu = ctx.blocks[menu_id]
    return next(iter(menu.fields._.values()))[0]
