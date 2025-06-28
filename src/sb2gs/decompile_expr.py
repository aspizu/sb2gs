from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich import print

from . import inputs, syntax

if TYPE_CHECKING:
    from .decompile_sprite import Ctx
    from .types import Block


MENUS = {
    "looks_costume": ("COSTUME", False),
}


def decompile_menu(ctx: Ctx, block: Block) -> None:
    input_name, is_input = MENUS[block.opcode]
    data = block.inputs if is_input else block.fields
    ctx.print(syntax.string(data._[input_name][0]))


@dataclass
class Operator:
    symbol: str
    precedence: int
    left_name: str
    right_name: str


# fmt:off
OPERATORS = { k: Operator(*v) for k, v in {
    #       OPCODE       | SYMBOL | PRECEDENCE |    LEFT    |    RIGHT    #
    #--------------------|--------|------------|------------|-------------#
    "operator_and"       :( "and" ,-1          , "OPERAND1" , "OPERAND2" ),
    "operator_or"        :( "or"  ,-1          , "OPERAND1" , "OPERAND2" ),
    "operator_not"       :( "not" , 0          , "OPERAND"  , ""         ),
    "operator_contains"  :( "in"  , 0          , "STRING2"  , "STRING1"  ),
    "operator_notequals" :( "!="  , 0          , "OPERAND1" , "OPERAND2" ),
    "operator_equals"    :( "=="  , 0          , "OPERAND1" , "OPERAND2" ),
    "operator_lt"        :( "<"   , 0          , "OPERAND1" , "OPERAND2" ),
    "operator_gt"        :( ">"   , 0          , "OPERAND1" , "OPERAND2" ),
    "operator_le"        :( "<="  , 0          , "OPERAND1" , "OPERAND2" ),
    "operator_ge"        :( ">="  , 0          , "OPERAND1" , "OPERAND2" ),
    "operator_join"      :( "&"   , 1          , "STRING1"  , "STRING2"  ),
    "operator_add"       :( "+"   , 1          , "NUM1"     , "NUM2"     ),
    "operator_subtract"  :( "-"   , 1          , "NUM1"     , "NUM2"     ),
    "operator_multiply"  :( "*"   , 2          , "NUM1"     , "NUM2"     ),
    "operator_divide"    :( "/"   , 2          , "NUM1"     , "NUM2"     ),
    "operator_mod"       :( "%"   , 2          , "NUM1"     , "NUM2"     ),
    "operator_letter_of" :( ""    , 3          , "LETTER"   , "STRING"   ),
    "negative"           :( "-"   , 3          , "NUM1"     , "NUM2"     ),
    }.items()}#----------|------------------------------------------------#
# fmt:on


def decompile_operand(ctx: Ctx, op_name: str, block: Block, op: Operator) -> None:
    from .decompile_input import decompile_input

    insert_parentheses = False
    operand_block = block.inputs._.get(op_name)
    if operand_id := inputs.block_id(operand_block):
        operand_block = ctx.blocks[operand_id]
        operand_op = OPERATORS.get(operand_block.opcode)
        insert_parentheses = operand_op and operand_op.precedence < op.precedence
    if insert_parentheses:
        ctx.print("(")
    decompile_input(ctx, op_name, block)
    if insert_parentheses:
        ctx.print(")")


def decompile_operator_letter_of(ctx: Ctx, block: Block) -> None:
    from .decompile_input import decompile_input

    op = OPERATORS[block.opcode]
    decompile_operand(ctx, op.right_name, block, op)
    ctx.print("[")
    decompile_input(ctx, op.left_name, block)
    ctx.print("]")


def decompile_binary_operator(ctx: Ctx, block: Block) -> None:
    op = OPERATORS[block.opcode]
    decompile_operand(ctx, op.left_name, block, op)
    ctx.print(" ", op.symbol, " ")
    decompile_operand(ctx, op.right_name, block, op)


def decompile_expr(ctx: Ctx, block: Block) -> None:
    print(block)
    if block.opcode in MENUS:
        decompile_menu(ctx, block)
        return
    if block.opcode == "operator_letter_of":
        decompile_operator_letter_of(ctx, block)
        return
    if block.opcode in OPERATORS:
        decompile_binary_operator(ctx, block)
        return
