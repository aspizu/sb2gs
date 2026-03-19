import builtins
import logging
from typing import TYPE_CHECKING, Any

from ._types import InputType

if TYPE_CHECKING:
    from ._types import Block
    from .decompile_sprite import Ctx

logger = logging.getLogger(__name__)


def block_id(input: builtins.list[Any] | None) -> str | None:
    if input is None:
        return None
    if isinstance(input[1], str):
        return input[1]
    return None


def block_value(input: builtins.list[Any] | None) -> int | float | str | None:
    if input is None:
        return None
    if not isinstance(input[1], builtins.list):
        return None
    if len(input[1]) < 2:
        return None
    value = input[1][1]
    logger.info(input)
    assert isinstance(value, (str, int, float))
    return value


def block(ctx: Ctx, block: Block, input_name: str) -> Block | None:
    if id := block_id(block.inputs._.get(input_name)):
        return ctx.blocks[id]
    return None


def variable(input: builtins.list[Any] | None) -> str | None:
    if input is None:
        return None
    if not isinstance(input[1], builtins.list):
        return None
    if len(input[1]) < 2:
        return None
    if input[1][0] != InputType.VAR:
        return None
    return input[1][1]


def list(input: builtins.list[Any] | None) -> str | None:
    if input is None:
        return None
    if not isinstance(input[1], builtins.list):
        return None
    if len(input[1]) < 2:
        return None
    if input[1][0] != InputType.LIST:
        return None
    return input[1][1]
