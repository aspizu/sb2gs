from __future__ import annotations

import contextlib
import logging
from copy import deepcopy
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from . import ast, inputs, syntax
from ._types import Signature
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
    "operator_letter_of" :( ""    , 1          , "LETTER"   , "STRING"   , Assoc.LEFT ),
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
    # Motion
    "motion_xposition":             _("x_position", []),
    "motion_yposition":             _("y_position", []),
    "motion_direction":             _("direction", []),
    # Looks
    "looks_size":                   _("size", []),
    "looks_costumenumbername":      _("costume_number", [], field="NUMBER_NAME",
                                    overloads={
                                        "number": "costume_number",
                                        "name": "costume_name",
                                    }),
    "looks_backdropnumbername":     _("backdrop_number", [], field="NUMBER_NAME",
                                    overloads={
                                        "number": "backdrop_number",
                                        "name": "backdrop_name",
                                    }),
    # Sound
    "sound_volume":                 _("volume", []),
    # Sensing
    "sensing_distanceto":           _("distance_to_mouse_pointer", [],
                                    menu="DISTANCETOMENU", field="DISTANCETOMENU",
                                    overloads={
                                        "_mouse_": "distance_to_mouse_pointer",
                                    }),
    "sensing_touchingobject":       _("touching_mouse_pointer", [],
                                    menu="TOUCHINGOBJECTMENU",
                                    field="TOUCHINGOBJECTMENU", overloads={
                                        "_mouse_": "touching_mouse_pointer",
                                        "_edge_": "touching_edge",
                                    }),
    "sensing_keypressed":           _("key_pressed", ["KEY_OPTION"], "KEY_OPTION",
                                      "KEY_OPTION", {}),
    "sensing_mousedown":            _("mouse_down", []),
    "sensing_mousex":               _("mouse_x", []),
    "sensing_mousey":               _("mouse_y", []),
    "sensing_loudness":             _("loudness", []),
    "sensing_timer":                _("timer", []),
    "sensing_current":              _("current_year", [], field="CURRENTMENU",
                                    overloads={
                                        "YEAR": "current_year",
                                        "MONTH": "current_month",
                                        "DATE": "current_date",
                                        "DAYOFWEEK": "current_day_of_week",
                                        "HOUR": "current_hour",
                                        "MINUTE": "current_minute",
                                        "SECOND": "current_second",
                                    }),
    "sensing_dayssince2000":        _("days_since_2000", []),
    "sensing_username":             _("username", []),
    "sensing_touchingcolor":        _("touching_color", ["COLOR"]),
    "sensing_coloristouchingcolor": _("color_is_touching_color", ["COLOR", "COLOR2"]),
    "sensing_answer":               _("answer", []),
    # Operator
    "operator_random":              _("random", ["FROM", "TO"]),
    "operator_length":              _("length", ["STRING"]),
    "operator_round":               _("round", ["NUM"]),
    "operator_mathop":              _("abs", ["NUM"], field="OPERATOR", overloads={
                                        "abs": "abs",
                                        "floor": "floor",
                                        "ceiling": "ceil",
                                        "sqrt": "sqrt",
                                        "sin": "sin",
                                        "cos": "cos",
                                        "tan": "tan",
                                        "asin": "asin",
                                        "acos": "acos",
                                        "atan": "atan",
                                        "ln": "ln",
                                        "log": "log",
                                        "e ^": "antiln",
                                        "10 ^": "antilog",
                                    }),
}
del _
# fmt: on


def decompile_block(ctx: Ctx, block: Block) -> None:
    from .decompile_input import decompile_input

    signature = deepcopy(BLOCKS[block.opcode])
    if signature.menu:
        ast.flatten_menu(ctx, block, signature.menu)
    if field := block.fields._.get(signature.field or ""):
        if opcode := unwrap(signature.overloads).get(field[0]):
            signature.opcode = opcode
            with contextlib.suppress(ValueError):
                signature.inputs.remove(unwrap(signature.field))
        else:
            block.inputs._[unwrap(signature.field)] = [1, [4, field[0]]]
    ctx.print(signature.opcode, "(")
    if signature.inputs:
        ctx.commasep(signature.inputs, decompile_input, pass_self=True, block=block)
    ctx.print(")")


UNARY_OPCODES = {"operator_letter_of", "operator_not"}


def decompile_expr(ctx: Ctx, block: Block) -> None:
    if block.opcode in MENUS:
        decompiler = decompile_menu
    elif block.opcode in OPERATORS and block.opcode not in UNARY_OPCODES:
        decompiler = decompile_binary_operator
    elif block.opcode in BLOCKS:
        decompiler = decompile_block
    else:
        decompiler = globals().get(f"decompile_{block.opcode}")
    if decompiler:
        logger.debug("using %s to decompile\n%s", decompiler, block)
        decompiler(ctx, block)
        return
    logger.error("no decompiler implemented for expr `%s`\n%s", block.opcode, block)
