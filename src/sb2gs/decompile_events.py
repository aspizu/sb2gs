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
        ctx.commasep(args, ctx.print)
    ctx.print(" ")
    decompile_stack(ctx, block.next)


def decompile_event(ctx: Ctx, block: Block) -> None:
    if decompiler := globals().get(f"decompile_{block.opcode}"):
        logger.debug("using %s to decompile\n%s", decompiler, block)
        decompiler(ctx, block)
        return
    logger.error("no decompiler implemented for event `%s`\n%s", block.opcode, block)


def decompile_events(ctx: Ctx) -> None:
    for block in ctx.blocks.values():
        if block.topLevel:
            decompile_event(ctx, block)
