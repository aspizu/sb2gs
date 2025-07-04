from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from . import custom_blocks, inputs, syntax
from .decompile_code import decompile_stack
from .utils import unwrap

if TYPE_CHECKING:
    from ._types import Block
    from .decompile_sprite import Ctx

logger = logging.getLogger(__name__)


def decompile_event_whenflagclicked(ctx: Ctx, block: Block) -> None:
    ctx.iprint("onflag ")
    decompile_stack(ctx, block.next)


def decompile_event_whenbroadcastreceived(ctx: Ctx, block: Block) -> None:
    ctx.iprint("on ", syntax.string(block.fields.BROADCAST_OPTION[0]), " ")
    decompile_stack(ctx, block.next)


def decompile_event_whenkeypressed(ctx: Ctx, block: Block) -> None:
    ctx.iprint("onkey ", syntax.string(block.fields.KEY_OPTION[0]), " ")
    decompile_stack(ctx, block.next)


def decompile_control_start_as_clone(ctx: Ctx, block: Block) -> None:
    ctx.iprint("onclone ")
    decompile_stack(ctx, block.next)


def decompile_event_whenthisspriteclicked(ctx: Ctx, block: Block) -> None:
    ctx.iprint("onclick ")
    decompile_stack(ctx, block.next)


def decompile_procedures_definition(ctx: Ctx, block: Block) -> None:
    custom = ctx.blocks[unwrap(inputs.block_id(block.inputs.custom_block))]
    args = json.loads(custom.mutation.argumentnames)
    logger.debug("custom block %s", custom)
    if custom.mutation.warp == "false":
        ctx.iprint("nowarp proc ")
    else:
        ctx.iprint("proc ")
    ctx.print(syntax.identifier(custom_blocks.get_name(custom)))
    if args:
        ctx.print(" ")
        ctx.commasep(args, lambda arg: ctx.print(syntax.identifier(arg)))
    ctx.print(" ")
    decompile_stack(ctx, block.next)


def decompile_event(ctx: Ctx, block: Block) -> None:
    from . import decompile_expr, decompile_stmt

    if decompiler := globals().get(f"decompile_{block.opcode}"):
        logger.debug("using %s to decompile\n%s", decompiler, block)
        decompiler(ctx, block)
        return
    if (
        block.opcode in decompile_stmt.BLOCKS
        or block.opcode in decompile_expr.BLOCKS
        or block.opcode in decompile_expr.OPERATORS
        or f"decompile_{block.opcode}" in decompile_stmt.__dict__
        or f"decompile_{block.opcode}" in decompile_expr.__dict__
    ):
        return
    logger.error("no decompiler implemented for event `%s`\n%s", block.opcode, block)


def decompile_events(ctx: Ctx) -> None:
    for block in ctx.blocks.values():
        if block.topLevel:
            decompile_event(ctx, block)
