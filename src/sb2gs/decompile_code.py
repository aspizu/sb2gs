from __future__ import annotations

from typing import TYPE_CHECKING

from .decompile_stmt import decompile_stmt

if TYPE_CHECKING:
    from .decompile_sprite import Ctx


def decompile_stack(ctx: Ctx, child: str | None) -> None:
    if child is None:
        ctx.println("{}")
        return
    ctx.println("{")
    with ctx.indent():
        while child:
            decompile_stmt(ctx, ctx.blocks[child])
            child = ctx.blocks[child].next
    ctx.iprintln("}")
