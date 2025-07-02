from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from . import ast, inputs, syntax
from ._types import Signature
from .decompile_input import decompile_input
from .utils import unwrap

if TYPE_CHECKING:
    from ._types import Block
    from .decompile_sprite import Ctx


logger = logging.getLogger(__name__)

MENUS = {
    "looks_costume": ("COSTUME", False),
}


def decompile_menu(ctx: Ctx, block: Block) -> None:
    input_name, is_input = MENUS[block.opcode]
    data = block.inputs if is_input else block.fields
    ctx.print(syntax.string(data._[input_name][0]))


class Assoc(StrEnum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


@dataclass
class Operator:
    symbol: str
    precedence: int
    left_name: str
    right_name: str
    assoc: Assoc


# fmt:off
OPERATORS = { k: Operator(*v) for k, v in {
    #       OPCODE       | SYMBOL | PRECEDENCE |    LEFT    |    RIGHT   |    ASSOC    #
    #--------------------|--------|------------|------------|--------------------------#
    "operator_not"       :( "not" , 1          , "OPERAND"  , ""         , Assoc.LEFT ),
    "operator_negative"  :( "-"   , 1          , ""         , "NUM"      , Assoc.RIGHT),
    "operator_multiply"  :( "*"   , 2          , "NUM1"     , "NUM2"     , Assoc.LEFT ),
    "operator_divide"    :( "/"   , 2          , "NUM1"     , "NUM2"     , Assoc.LEFT ),
    "operator_mod"       :( "%"   , 2          , "NUM1"     , "NUM2"     , Assoc.LEFT ),
    "operator_add"       :( "+"   , 3          , "NUM1"     , "NUM2"     , Assoc.LEFT ),
    "operator_subtract"  :( "-"   , 3          , "NUM1"     , "NUM2"     , Assoc.LEFT ),
    "operator_lt"        :( "<"   , 4          , "OPERAND1" , "OPERAND2" , Assoc.LEFT ),
    "operator_le"        :( "<="  , 4          , "OPERAND1" , "OPERAND2" , Assoc.LEFT ),
    "operator_gt"        :( ">"   , 4          , "OPERAND1" , "OPERAND2" , Assoc.LEFT ),
    "operator_ge"        :( ">="  , 4          , "OPERAND1" , "OPERAND2" , Assoc.LEFT ),
    "operator_join"      :( "&"   , 5          , "STRING1"  , "STRING2"  , Assoc.LEFT ),
    "operator_contains"  :( "in"  , 6          , "STRING2"  , "STRING1"  , Assoc.LEFT ),
    "operator_equals"    :( "=="  , 6          , "OPERAND1" , "OPERAND2" , Assoc.LEFT ),
    "operator_notequals" :( "!="  , 6          , "OPERAND1" , "OPERAND2" , Assoc.LEFT ),
    "operator_and"       :( "and" , 7          , "OPERAND1" , "OPERAND2" , Assoc.LEFT ),
    "operator_or"        :( "or"  , 8          , "OPERAND1" , "OPERAND2" , Assoc.LEFT ),
    }.items()}#----------|-------------------------------------------------------------#
# fmt:on


def is_parenthesis_required(
    parent_op: Operator, child_op: Operator, assoc: Assoc
) -> bool:
    if child_op.precedence > parent_op.precedence:
        return True
    return child_op.precedence == parent_op.precedence and parent_op.assoc != assoc


def decompile_operand(ctx: Ctx, op_name: str, block: Block, assoc: Assoc) -> None:
    from .decompile_input import decompile_input

    op = OPERATORS[block.opcode]
    parenthesis = False
    operand_block = block.inputs._.get(op_name)
    if operand_id := inputs.block_id(operand_block):
        operand_block = ctx.blocks[operand_id]
        operand_op = OPERATORS.get(operand_block.opcode)
        parenthesis = operand_op and is_parenthesis_required(op, operand_op, assoc)
    if parenthesis:
        ctx.print("(")
    decompile_input(ctx, op_name, block)
    if parenthesis:
        ctx.print(")")


def decompile_operator_not(ctx: Ctx, block: Block) -> None:
    ctx.print("not ")
    decompile_operand(ctx, "OPERAND", block, Assoc.LEFT)


def decompile_operator_letter_of(ctx: Ctx, block: Block) -> None:
    from .decompile_input import decompile_input

    op = OPERATORS[block.opcode]
    decompile_operand(ctx, op.right_name, block, Assoc.LEFT)
    ctx.print("[")
    decompile_input(ctx, op.left_name, block)
    ctx.print("]")


def decompile_binary_operator(ctx: Ctx, block: Block) -> None:
    op = OPERATORS[block.opcode]
    decompile_operand(ctx, op.left_name, block, Assoc.LEFT)
    ctx.print(" ", op.symbol, " ")
    decompile_operand(ctx, op.right_name, block, Assoc.RIGHT)


# fmt: off
_ = Signature
BLOCKS = {

}
del _
# fmt: on


def decompile_block(ctx: Ctx, block: Block) -> None:
    signature = deepcopy(BLOCKS[block.opcode])
    if signature.menu:
        ast.flatten_menu(ctx, block, signature.menu)
    if field := block.fields._.get(signature.field or ""):
        if opcode := unwrap(signature.overloads).get(field[0]):
            signature.opcode = opcode
            signature.inputs.remove(unwrap(signature.field))
        else:
            block.inputs._[unwrap(signature.field)] = [1, [4, field[0]]]
    ctx.print(signature.opcode, "(")
    if signature.inputs:
        ctx.commasep(signature.inputs, decompile_input, pass_self=True, block=block)
    ctx.print(")")


def decompile_expr(ctx: Ctx, block: Block) -> None:
    if block.opcode in MENUS:
        decompiler = decompile_menu
    elif block.opcode in OPERATORS:
        decompiler = decompile_binary_operator
    else:
        decompiler = globals().get(f"decompile_{block.opcode}")
    if decompiler:
        logger.debug("using %s to decompile\n%s", decompiler, block)
        decompiler(ctx, block)
        return
    logger.error("no decompiler implemented for expr `%s`\n%s", block.opcode, block)
