from __future__ import annotations

from typing import TYPE_CHECKING

from . import inputs

if TYPE_CHECKING:
    from ._types import Block
    from .decompile_sprite import Ctx


def flatten_menu(ctx: Ctx, block: Block, menu_name: str) -> None:
    menu_id = inputs.block_id(block.inputs._.get(menu_name))
    if menu_id is None:
        return
    menu = ctx.blocks[menu_id]
    block.fields._.update(menu.fields._)
