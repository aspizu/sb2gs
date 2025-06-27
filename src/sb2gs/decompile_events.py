from __future__ import annotations

from typing import TYPE_CHECKING

from .decompile_code import decompile_stack

if TYPE_CHECKING:
    from .decompile_sprite import Ctx
    from .types import Block


def decompile_onflag(ctx: Ctx, block: Block) -> None:
    ctx.iprint("onflag ")
    decompile_stack(ctx, block.next)


def decompile_events(ctx: Ctx) -> None:
    for block in ctx.blocks.values():
        if block.topLevel:
            {"event_whenflagclicked": decompile_onflag}[block.opcode](ctx, block)
