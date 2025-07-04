from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from . import inputs, syntax
from ._types import InputType
from .decompile_expr import decompile_expr

if TYPE_CHECKING:
    from ._types import Block
    from .decompile_sprite import Ctx

logger = logging.getLogger(__name__)


def decompile_input(ctx: Ctx, input_name: str, block: Block) -> None:
    input = block.inputs._.get(input_name)
    if input is None or input == [1, None]:
        ctx.print("false")
        return
    if block_id := inputs.block_id(input):
        decompile_expr(ctx, ctx.blocks[block_id])
        return
    input_type = InputType(input[1][0])
    input_value: str = input[1][1]
    assert isinstance(input_value, str)
    if input_type in {InputType.VAR, InputType.LIST}:
        ctx.print(syntax.identifier(input_value))
        return
    ctx.print(syntax.value(input_value))
