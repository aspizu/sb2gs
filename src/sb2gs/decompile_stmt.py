from __future__ import annotations

import contextlib
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
    "motion_goto":              _("goto", ["TO"], menu="TO", field="TO", overloads={
                                    "_mouse_": "goto_mouse_pointer",
                                    "_random_": "goto_random_position",
                                }),
    "motion_gotoxy":            _("goto", ["X", "Y"]),
    "motion_glidesecstoxy":     _("glide", ["X", "Y", "SECS"]),
    "motion_glideto":           _("glide", ["TO", "SECS"], menu="TO", field="TO",
                                overloads={
                                    "_mouse_": "glide_to_mouse_pointer",
                                    "_random_": "glide_to_random_position",
                                }),
    "motion_pointindirection":  _("point_in_direction", ["DIRECTION"]),
    "motion_pointtowards":      _("point_towards", ["TOWARDS"], menu="TOWARDS",
                                field="TOWARDS", overloads={
                                    "_mouse_": "point_towards_mouse_pointer",
                                    "_random_": "point_towards_random_direction",
                                }),
    "motion_changexby":         _("change_x", ["DX"]),
    "motion_setx":              _("set_x", ["X"]),
    "motion_changeyby":         _("change_y", ["DY"]),
    "motion_sety":              _("set_y", ["Y"]),
    "motion_ifonedgebounce":    _("if_on_edge_bounce", []),
    "motion_setrotationstyle":  _("set_rotation_style_all_around", [],
                                field="STYLE", overloads={
                                    "left-right": "set_rotation_style_left_right",
                                    "don't rotate": "set_rotation_style_do_not_rotate",
                                    "all around": "set_rotation_style_all_around",
                                }),
    # Looks
    "looks_sayforsecs":         _("say", ["MESSAGE", "SECS"]),
    "looks_thinkforsecs":       _("think", ["MESSAGE", "SECS"]),
    "looks_say":                _("say", ["MESSAGE"]),
    "looks_think":              _("think", ["MESSAGE"]),
    "looks_switchcostumeto":    _("switch_costume", ["COSTUME"]),
    "looks_nextcostume":        _("next_costume", []),
    "looks_switchbackdropto":   _("switch_backdrop", ["BACKDROP"], menu="BACKDROP",
                                field="BACKDROP", overloads={
                                    "next backdrop": "next_backdrop",
                                    "previous backdrop": "previous_backdrop",
                                    "random backdrop": "random_backdrop",
                                }),
    "looks_nextbackdrop":       _("next_backdrop", []),
    "looks_setsizeto":          _("set_size", ["SIZE"]),
    "looks_changesizeby":       _("change_size", ["CHANGE"]),
    "looks_changeeffectby":     _("change_color_effect", ["CHANGE"],
                                field="EFFECT", overloads={
                                    "COLOR": "change_color_effect",
                                    "FISHEYE": "change_fisheye_effect",
                                    "WHIRL": "change_whirl_effect",
                                    "PIXELATE": "change_pixelate_effect",
                                    "MOSAIC": "change_mosaic_effect",
                                    "BRIGHTNESS": "change_brightness_effect",
                                    "GHOST": "change_ghost_effect",
                                }),
    "looks_seteffectto":        _("set_color_effect", ["VALUE"],
                                field="EFFECT", overloads={
                                    "COLOR": "set_color_effect",
                                    "FISHEYE": "set_fisheye_effect",
                                    "WHIRL": "set_whirl_effect",
                                    "PIXELATE": "set_pixelate_effect",
                                    "MOSAIC": "set_mosaic_effect",
                                    "BRIGHTNESS": "set_brightness_effect",
                                    "GHOST": "set_ghost_effect",
                                }),
    "looks_cleargraphiceffects":_("clear_graphic_effects", []),
    "looks_show":               _("show", []),
    "looks_hide":               _("hide", []),
    "looks_gotofrontback":      _("goto_front", [], field="FRONT_BACK", overloads={
                                    "front": "goto_front",
                                    "back": "goto_back",
                                }),
    "looks_goforwardbackwardlayers": _("go_forward", ["NUM"],
                                field="FORWARD_BACKWARD", overloads={
                                    "forward": "go_forward",
                                    "backward": "go_backward",
                                }),
    # Sound
    "sound_playuntildone":      _("play_sound_until_done", ["SOUND_MENU"], "SOUND_MENU",
                                  "SOUND_MENU", {}),
    "sound_play":               _("start_sound", ["SOUND_MENU"], "SOUND_MENU",
                                  "SOUND_MENU", {}),
    "sound_stopallsounds":      _("stop_all_sounds", []),
    "sound_changeeffectby":     _("change_pitch_effect", ["VALUE"],
                                field="EFFECT", overloads={
                                    "PITCH": "change_pitch_effect",
                                    "PAN": "change_pan_effect",
                                }),
    "sound_seteffectto":        _("set_pitch_effect", ["VALUE"],
                                field="EFFECT", overloads={
                                    "PITCH": "set_pitch_effect",
                                    "PAN": "set_pan_effect",
                                }),
    "sound_changevolumeby":     _("change_volume", ["VOLUME"]),
    "sound_setvolumeto":        _("set_volume", ["VOLUME"]),
    "sound_cleareffects":       _("clear_sound_effects", []),
    # Event
    "event_broadcast":          _("broadcast", ["BROADCAST_INPUT"]),
    "event_broadcastandwait":   _("broadcast_and_wait", ["BROADCAST_INPUT"]),
    # Control
    "control_wait":             _("wait", ["DURATION"]),
    "control_stop":             _("stop_all", [], field="STOP_OPTION", overloads={
                                    "all": "stop_all",
                                    "this script": "stop_this_script",
                                    "other scripts in sprite": "stop_other_scripts",
                                }),
    "control_delete_this_clone":_("delete_this_clone", []),
    "control_create_clone_of":  _("clone", ["CLONE_OPTION"], menu="CLONE_OPTION",
                                field="CLONE_OPTION", overloads={
                                    "_myself_": "clone",
                                }),
    # Sensing
    "sensing_askandwait":       _("ask", ["QUESTION"]),
    "sensing_setdragmode":      _("set_drag_mode_draggable", [],
                                field="DRAG_MODE", overloads={
                                    "draggable": "set_drag_mode_draggable",
                                    "not draggable": "set_drag_mode_not_draggable",
                                }),
    "sensing_resettimer":       _("reset_timer", []),
    # Pen
    "pen_clear":                _("erase_all", []),
    "pen_stamp":                _("stamp", []),
    "pen_penDown":              _("pen_down", []),
    "pen_penUp":                _("pen_up", []),
    "pen_setPenColorToColor":   _("set_pen_color", ["COLOR"]),
    "pen_changePenSizeBy":      _("change_pen_size", ["SIZE"]),
    "pen_setPenSizeTo":         _("set_pen_size", ["SIZE"]),
    "pen_setPenColorParamTo":   _("set_pen_hue", ["VALUE"],
                                field="COLOR_PARAM", overloads={
                                    "color": "set_pen_hue",
                                    "saturation": "set_pen_saturation",
                                    "brightness": "set_pen_brightness",
                                    "transparency": "set_pen_transparency",
                                }),
    "pen_changePenColorParamBy":_("change_pen_hue", ["VALUE"],
                                field="COLOR_PARAM", overloads={
                                    "color": "change_pen_hue",
                                    "saturation": "change_pen_saturation",
                                    "brightness": "change_pen_brightness",
                                    "transparency": "change_pen_transparency",
                                }),
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
            with contextlib.suppress(ValueError):
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


def decompile_control_repeat_until(ctx: Ctx, block: Block) -> None:
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


def decompile_data_setvariableto(ctx: Ctx, block: Block) -> None:
    ctx.iprint(syntax.identifier(block.fields.VARIABLE[0]), " = ")
    decompile_input(ctx, "VALUE", block)
    ctx.println(";")


def decompile_data_changevariableby(ctx: Ctx, block: Block) -> None:
    op = block._.get("OPERATOR", "+")
    ctx.iprint(syntax.identifier(block.fields.VARIABLE[0]), f" {op}= ")
    decompile_input(ctx, "VALUE", block)
    ctx.println(";")


def decompile_data_showvariable(ctx: Ctx, block: Block) -> None:
    ctx.iprintln("show ", syntax.identifier(block.fields.VARIABLE[0]), ";")


def decompile_data_hidevariable(ctx: Ctx, block: Block) -> None:
    ctx.iprintln("hide ", syntax.identifier(block.fields.VARIABLE[0]), ";")


def decompile_data_addtolist(ctx: Ctx, block: Block) -> None:
    ctx.iprint("add ")
    decompile_input(ctx, "ITEM", block)
    ctx.println(" to ", syntax.identifier(block.fields.LIST[0]), ";")


def decompile_data_deleteoflist(ctx: Ctx, block: Block) -> None:
    ctx.print("delete ", syntax.identifier(block.fields.LIST[0]), "[")
    decompile_input(ctx, "INDEX", block)
    ctx.println("];")


def decompile_data_deletealloflist(ctx: Ctx, block: Block) -> None:
    ctx.iprint("delete ")
    ctx.print(syntax.identifier(block.fields.LIST[0]))
    ctx.println(";")


def decompile_data_insertatlist(ctx: Ctx, block: Block) -> None:
    ctx.iprint("insert ")
    decompile_input(ctx, "ITEM", block)
    ctx.print(" at ", syntax.identifier(block.fields.LIST[0]), "[")
    decompile_input(ctx, "INDEX", block)
    ctx.println("];")


def decompile_data_replaceitemoflist(ctx: Ctx, block: Block) -> None:
    ctx.iprint(syntax.identifier(block.fields.LIST[0]), "[")
    decompile_input(ctx, "INDEX", block)
    op = block._.get("OPERATOR", "")
    ctx.print(f"] {op}= ")
    decompile_input(ctx, "ITEM", block)
    ctx.println(";")


def decompile_data_showlist(ctx: Ctx, block: Block) -> None:
    ctx.iprintln("show ", syntax.identifier(block.fields.LIST[0]), ";")


def decompile_data_hidelist(ctx: Ctx, block: Block) -> None:
    ctx.iprintln("hide ", syntax.identifier(block.fields.LIST[0]), ";")


decompile_control_wait_until = decompile_control_repeat_until
decompile_control_if_else = decompile_control_if


def decompile_stmt(ctx: Ctx, block: Block) -> None:
    if (mutation := block._.get("mutation")) and mutation._.get("proccode") in ADDONS:
        decompiler = decompile_addon
    elif block.opcode in BLOCKS:
        decompiler = decompile_block
    else:
        decompiler = globals().get(f"decompile_{block.opcode}")
    if decompiler:
        logger.debug("using %s to decompile\n%s", decompiler, block)
        decompiler(ctx, block)
        return
    logger.error("no decompiler implemented for stmt `%s`\n%s", block.opcode, block)
