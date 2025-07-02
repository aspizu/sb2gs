from __future__ import annotations

import json
import logging
from copy import deepcopy
from typing import TYPE_CHECKING

from . import ast, custom_blocks, inputs, syntax
from ._types import Block, Signature
from .decompile_input import decompile_input
from .json_object import JSONObject
from .utils import unwrap

if TYPE_CHECKING:
    from .decompile_sprite import Ctx

logger = logging.getLogger(__name__)


# fmt: off
_ = Signature
BLOCKS = {
    # Motion
    "motion_movesteps":         _("move", ["STEPS"]),
    "motion_turnleft":          _("turn_left", ["DEGREES"]),
    "motion_turnright":         _("turn_right", ["DEGREES"]),
    "motion_gotoxy":            _("goto", ["X", "Y"]),
    "motion_glidesecstoxy":     _("glide", ["X", "Y", "SECS"]),
    "motion_pointindirection":  _("point_in_direction", ["DIRECTION"]),
    "motion_changexby":         _("change_x", ["DX"]),
    "motion_setx":              _("set_x", ["X"]),
    "motion_changeyby":         _("change_y", ["DY"]),
    "motion_sety":              _("set_y", ["Y"]),
    "motion_ifonedgebounce":    _("if_on_edge_bounce", []),
    "motion_goto":              _("goto", ["TO"], menu="TO", field="TO", overloads={
                                    "_mouse_": "goto_mouse_pointer",
                                    "_random_": "goto_random_position",
                                }),
    # Looks
    "looks_sayforsecs":         _("say", ["MESSAGE", "SECS"]),
    "looks_thinkforsecs":       _("think", ["MESSAGE", "SECS"]),
    "looks_say":                _("say", ["MESSAGE"]),
    "looks_think":              _("think", ["MESSAGE"]),
    "looks_switchcostumeto":    _("switch_costume", ["COSTUME"]),
    "looks_nextcostume":        _("next_costume", []),
    "looks_nextbackdrop":       _("next_backdrop", []),
    "looks_setsizeto":          _("set_size", ["SIZE"]),
    "looks_changesizeby":       _("change_size", ["CHANGE"]),
    "looks_cleargraphiceffects":_("clear_graphic_effects", []),
    "looks_show":               _("show", []),
    "looks_hide":               _("hide", []),
    # Sound
    "sound_playuntildone":      _("play_sound_until_done", ["SOUND_MENU"]),
    "sound_play":               _("start_sound", ["SOUND_MENU"]),
    "sound_stopallsounds":      _("stop_all_sounds", []),
    "sound_changevolumeby":     _("change_volume", ["VOLUME"]),
    "sound_setvolumeto":        _("set_volume", ["VOLUME"]),
    "sound_cleareffects":       _("clear_sound_effects", []),
    # Event
    "event_broadcast":          _("broadcast", ["BROADCAST_INPUT"]),
    "event_broadcastandwait":   _("broadcast_and_wait", ["BROADCAST_INPUT"]),
    # Control
    "control_wait":             _("wait", ["DURATION"]),
    "control_delete_this_clone":_("delete_this_clone", []),
    # Sensing
    "sensing_askandwait":       _("ask", ["QUESTION"]),
    "sensing_resettimer":       _("reset_timer", []),
    # Pen
    "pen_clear":                _("erase_all", []),
    "pen_stamp":                _("stamp", []),
    "pen_penDown":              _("pen_down", []),
    "pen_penUp":                _("pen_up", []),
    "pen_setPenColorToColor":   _("set_pen_color", ["COLOR"]),
    "pen_changePenSizeBy":      _("change_pen_size", ["SIZE"]),
    "pen_setPenSizeTo":         _("set_pen_size", ["SIZE"]),
    # Music
    "music_restForBeats":       _("rest", ["BEATS"]),
    "music_setTempo":           _("set_tempo", ["TEMPO"]),
    "music_changeTempo":        _("change_tempo", ["TEMPO"]),
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
    ctx.iprint(signature.opcode)
    if signature.inputs:
        ctx.print(" ")
        ctx.commasep(signature.inputs, decompile_input, pass_self=True, block=block)
    ctx.println(";")


ADDONS = {
    "\u200b\u200bbreakpoint\u200b\u200b": ("breakpoint", []),
    "\u200b\u200blog\u200b\u200b %s": ("log", ["arg0"]),
    "\u200b\u200bwarn\u200b\u200b %s": ("warn", ["arg0"]),
    "\u200b\u200berror\u200b\u200b %s": ("error", ["arg0"]),
}


def decompile_addon(ctx: Ctx, block: Block) -> None:
    opcode, inputs = ADDONS[block.mutation.proccode]
    ctx.iprint(opcode)
    if inputs:
        ctx.print(" ")
        ctx.commasep(inputs, decompile_input, pass_self=True, block=block)
    ctx.println(";")


def decompile_else(ctx: Ctx, block_id: str | None) -> None:
    from .decompile_code import decompile_stack

    if block_id is None:
        return
    block = ctx.blocks[block_id]
    if block.opcode.startswith("control_if") and block.next is None:
        ctx.iprint("elif ")
        decompile_input(ctx, "CONDITION", block)
        ctx.print(" ")
        decompile_stack(ctx, inputs.block_id(block.inputs._.get("SUBSTACK")))
        decompile_else(ctx, inputs.block_id(block.inputs._.get("SUBSTACK2")))
    else:
        ctx.iprint("else ")
        decompile_stack(ctx, block_id)


def decompile_control_if(ctx: Ctx, block: Block) -> None:
    from .decompile_code import decompile_stack

    ctx.iprint("if ")
    decompile_input(ctx, "CONDITION", block)
    ctx.print(" ")
    decompile_stack(ctx, inputs.block_id(block.inputs._.get("SUBSTACK")))
    decompile_else(ctx, inputs.block_id(block.inputs._.get("SUBSTACK2")))


def decompile_control_repeat(ctx: Ctx, block: Block) -> None:
    from .decompile_code import decompile_stack

    ctx.iprint("repeat ")
    decompile_input(ctx, "TIMES", block)
    ctx.print(" ")
    decompile_stack(ctx, inputs.block_id(block.inputs._.get("SUBSTACK")))


def decompile_repeat_until(ctx: Ctx, block: Block) -> None:
    from .decompile_code import decompile_stack

    ctx.iprint("until ")
    decompile_input(ctx, "CONDITION", block)
    ctx.print(" ")
    decompile_stack(ctx, inputs.block_id(block.inputs._.get("SUBSTACK")))


def decompile_control_forever(ctx: Ctx, block: Block) -> None:
    from .decompile_code import decompile_stack

    ctx.iprint("forever ")
    decompile_stack(ctx, inputs.block_id(block.inputs._.get("SUBSTACK")))


def decompile_control_while(ctx: Ctx, block: Block) -> None:
    from .decompile_code import decompile_stack
    from .decompile_expr import Assoc, decompile_operand

    condition = inputs.block_id(block.inputs._.get("CONDITION"))

    if condition:
        ctx.iprint("until not ")
        decompile_operand(
            ctx,
            "OPERAND",
            Block("operator_not", inputs=JSONObject({"OPERAND": [2, condition]})),
            Assoc.LEFT,
        )
        ctx.print(" ")
    else:
        ctx.iprint("until not true ")
    decompile_stack(ctx, inputs.block_id(block.inputs._.get("SUBSTACK")))


def decompile_procedures_call(ctx: Ctx, block: Block) -> None:
    ctx.iprint(syntax.identifier(custom_blocks.get_name(block)))
    args = json.loads(block.mutation.argumentids)
    if args:
        ctx.print(" ")
        ctx.commasep(args, decompile_input, pass_self=True, block=block)
    ctx.println(";")


def decompile_stmt(ctx: Ctx, block: Block) -> None:
    if (mutation := block._.get("mutation")) and mutation.proccode in ADDONS:
        decompiler = decompile_addon
    elif block.opcode in BLOCKS:
        decompiler = decompile_block
    elif block.opcode in {"control_wait_until", "control_repeat_until"}:
        decompiler = decompile_repeat_until
    else:
        decompiler = globals().get(f"decompile_{block.opcode}")
    if decompiler:
        logger.debug("using %s to decompile\n%s", decompiler, block)
        decompiler(ctx, block)
        return
    logger.error("no decompiler implemented for stmt `%s`\n%s", block.opcode, block)
