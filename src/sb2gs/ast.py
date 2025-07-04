from __future__ import annotations

import functools
import logging
from typing import TYPE_CHECKING, Any

from . import inputs
from .decompile_expr import OPERATORS

if TYPE_CHECKING:
    from collections.abc import Callable

    from ._types import Block
    from .decompile_sprite import Ctx

logger = logging.getLogger(__name__)


type Transformer = Callable[[Ctx, Block], None]


transformers: list[Transformer] = []


def transformer(opcode: str) -> Callable[[Transformer], Transformer]:
    def decorator(func: Transformer) -> Transformer:
        @functools.wraps(func)
        def wrapper(ctx: Ctx, block: Block) -> None:
            if block.opcode != opcode:
                return
            func(ctx, block)

        transformers.append(wrapper)
        return wrapper

    return decorator


def compare_inputs(
    ctx: Ctx,
    input1: list[Any] | None,
    input2: list[Any] | None,
) -> bool:
    input1_block_id = inputs.block_id(input1)
    input2_block_id = inputs.block_id(input2)
    if not compare_tree(
        ctx,
        None if input1_block_id is None else ctx.blocks[input1_block_id],
        None if input2_block_id is None else ctx.blocks[input2_block_id],
    ):
        return False
    input1_value = inputs.block_value(input1)
    input2_value = inputs.block_value(input2)
    return input1_value == input2_value


def compare_tree(ctx: Ctx, node1: Block | None, node2: Block | None) -> bool:
    if node1 is None or node2 is None:
        return node1 == node2
    if node1.opcode != node2.opcode:
        return False
    if node1.fields._ != node2.fields._:
        return False
    for node1_input_name, node1_input_value in node1.inputs._.items():
        node2_input_value = node2.inputs._.get(node1_input_name)
        if node2_input_value is None:
            return False
        if not compare_inputs(ctx, node1_input_value, node2_input_value):
            return False

    return True


def flatten_menu(ctx: Ctx, block: Block, menu_name: str) -> None:
    menu_id = inputs.block_id(block.inputs._.get(menu_name))
    if menu_id is None:
        return
    menu = ctx.blocks[menu_id]
    block.fields._.update(menu.fields._)


@transformer("data_listcontainsitem")
def transform_list_contains_to_item_num(_ctx: Ctx, block: Block) -> None:
    block.opcode = "data_itemnumoflist"


@transformer("operator_subtract")
def transform_subtract_zero_to_negative(_ctx: Ctx, block: Block) -> None:
    if inputs.block_value(block.inputs.NUM1) in {"", "0", "0.0"}:
        block.opcode = "operator_negative"


@transformer("data_changevariableby")
def transform_change_variable_by_negative(ctx: Ctx, block: Block) -> None:
    if not (
        (operand := inputs.block(ctx, block, "VALUE"))
        and operand.opcode in {"operator_subtract", "operator_negative"}
        and inputs.block_value(operand.inputs.NUM1) in {"", "0", "0.0"}
    ):
        return
    block._["OPERATOR"] = "-"
    block.inputs._["VALUE"] = operand.inputs.NUM2


ARITHMETIC_OPCODES = {
    "operator_add",
    "operator_subtract",
    "operator_multiply",
    "operator_divide",
    "operator_mod",
}


@transformer("data_setvariableto")
def transform_augmented_set_variable(ctx: Ctx, block: Block) -> None:
    if not (
        (operand := inputs.block(ctx, block, "VALUE"))
        and operand.opcode in ARITHMETIC_OPCODES
        and inputs.variable(operand.inputs.NUM1) == block.fields.VARIABLE[0]
    ):
        return
    block.opcode = "data_changevariableby"
    block._["OPERATOR"] = OPERATORS[operand.opcode].symbol
    block.inputs._["VALUE"] = operand.inputs.NUM2


@transformer("data_setvariableto")
def transform_augmented_set_variable_join(ctx: Ctx, block: Block) -> None:
    if not (
        (operand := inputs.block(ctx, block, "VALUE"))
        and operand.opcode == "operator_join"
        and inputs.variable(operand.inputs.STRING1) == block.fields.VARIABLE[0]
    ):
        return
    block.opcode = "data_changevariableby"
    block._["OPERATOR"] = "&"
    block.inputs._["VALUE"] = operand.inputs.STRING2


@transformer("data_replaceitemoflist")
def transform_augmented_replace_list_item(ctx: Ctx, block: Block) -> None:
    if not (
        (operand := inputs.block(ctx, block, "ITEM"))
        and operand.opcode in ARITHMETIC_OPCODES
        and (lhs := inputs.block(ctx, operand, "NUM1"))
        and lhs.opcode == "data_itemoflist"
        and lhs.fields.LIST[0] == block.fields.LIST[0]
        and compare_inputs(
            ctx,
            block.inputs._.get("INDEX"),
            lhs.inputs._.get("INDEX"),
        )
    ):
        return
    block._["OPERATOR"] = OPERATORS[operand.opcode].symbol
    block.inputs._["ITEM"] = operand.inputs.NUM2


@transformer("data_replaceitemoflist")
def transform_augmented_replace_list_item_join(ctx: Ctx, block: Block) -> None:
    if not (
        (operand := inputs.block(ctx, block, "ITEM"))
        and operand.opcode == "operator_join"
        and (lhs := inputs.block(ctx, operand, "STRING1"))
        and lhs.opcode == "data_itemoflist"
        and lhs.fields.LIST[0] == block.fields.LIST[0]
        and compare_tree(
            ctx,
            inputs.block(ctx, block, "INDEX"),
            inputs.block(ctx, lhs, "INDEX"),
        )
    ):
        return
    block._["OPERATOR"] = "&"
    block.inputs._["ITEM"] = operand.inputs.STRING2


def transform_block(ctx: Ctx, block: Block) -> None:
    for transformer in transformers:
        transformer(ctx, block)


def transform(ctx: Ctx) -> None:
    for block in ctx.blocks.values():
        if isinstance(block, list):
            continue
        transform_block(ctx, block)
