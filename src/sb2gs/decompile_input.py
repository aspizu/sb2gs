from __future__ import annotations

from typing import TYPE_CHECKING

from rich import print

from .decompile_code import decompile_value

if TYPE_CHECKING:
    from .decompile_sprite import Ctx
    from .types import Block


def decompile_input(ctx: Ctx, block: Block, input_name: str) -> None:
    input = block.inputs._[input_name]
    if input[0] == 1 and input[1][0] == 4:
        decompile_value(ctx, input[1][1])
    print(input)
