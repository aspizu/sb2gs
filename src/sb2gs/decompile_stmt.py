from __future__ import annotations

from typing import TYPE_CHECKING

from .decompile_input import decompile_input

if TYPE_CHECKING:
    from .decompile_sprite import Ctx
    from .types import Block


def decompile_stmt(ctx: Ctx, block: Block) -> None:
    if block.opcode == "motion_movesteps":
        ctx.iprint("move ")
        decompile_input(ctx, block, "STEPS")
        ctx.println(";")
