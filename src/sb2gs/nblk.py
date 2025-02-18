# new blocks lists

from __future__ import annotations

import typing
from dataclasses import dataclass
from typing import Callable

from sb2gs.sb3 import Block

if typing.TYPE_CHECKING:
    from sb2gs.decompiler import Blocks


@dataclass
class Prototype:
    name: str
    args: list[str]


class Option[T]:
    def __init__(self, value: T | None):
        self.value: T | None = value

    def is_some_and(self, f: Callable[[T], bool]) -> bool:
        return self.value is not None and f(self.value)


nblocks = {
    # Motion
    "motion_movesteps": Prototype("move", ["STEPS"]),
    "motion_turnleft": Prototype("turn_left", ["DEGREES"]),
    "motion_turnright": Prototype("turn_right", ["DEGREES"]),
    "motion_gotoxy": Prototype("goto", ["X", "Y"]),
    "motion_glidesecstoxy": Prototype("glide", ["X", "Y"]),
    "motion_pointindirection": Prototype("point_in_direction", ["DIRECTION"]),
    "motion_changexby": Prototype("change_x", ["DX"]),
    "motion_setx": Prototype("set_x", ["X"]),
    "motion_changeyby": Prototype("change_y", ["DY"]),
    "motion_sety": Prototype("set_y", ["Y"]),
    "motion_ifonedgebounce": Prototype("if_on_edge_bounce", []),
    # Looks
    "looks_sayforsecs": Prototype("say", ["MESSAGE", "SECS"]),
    "looks_thinkforsecs": Prototype("think", ["MESSAGE", "SECS"]),
    "looks_say": Prototype("say", ["MESSAGE"]),
    "looks_think": Prototype("think", ["MESSAGE"]),
    "looks_switchcostumeto": Prototype("switch_costume", ["COSTUME"]),
    "looks_nextcostume": Prototype("next_costume", []),
    "looks_switchbackdropto": Prototype("switch_backdrop", ["BACKDROP"]),
    "looks_nextbackdrop": Prototype("next_backdrop", []),
    "looks_setsizeto": Prototype("set_size", ["SIZE"]),
    "looks_changesizeby": Prototype("change_size", ["CHANGE"]),
    "looks_cleargraphiceffects": Prototype("clear_graphic_effects", []),
    "looks_show": Prototype("show", []),
    "looks_hide": Prototype("hide", []),
    # TODO: Implement sound blocks
    # Event
    "event_broadcast": Prototype("broadcast", ["BROADCAST_INPUT"]),
    "event_broadcastandwait": Prototype("broadcast_and_wait", ["BROADCAST_INPUT"]),
    # Control
    "control_wait": Prototype("wait", ["DURATION"]),
    "control_wait_until": Prototype("wait_until", ["CONDITION"]),
    "control_delete_this_clone": Prototype("delete_this_clone", []),
    # Sensing
    "sensing_askandwait": Prototype("ask", ["QUESTION"]),
    "sensing_resettimer": Prototype("reset_timer", []),
    # Pen
    "pen_clear": Prototype("erase_all", []),
    "pen_stamp": Prototype("stamp", []),
    "pen_penDown": Prototype("pen_down", []),
    "pen_penUp": Prototype("pen_up", []),
    "pen_setPenColorToColor": Prototype("set_pen_color", ["COLOR"]),
    "pen_changePenSizeBy": Prototype("change_pen_size", ["SIZE"]),
    "pen_setPenSizeTo": Prototype("set_pen_size", ["SIZE"]),
}


def getmenu(
    blocks: Blocks, block: Block, input: str, menu_opcode: str, field: str | None = None
):
    field = field or input
    INPUT = block.inputs[input]
    if INPUT[0] == 1:
        menu = blocks.blocks[INPUT[1]]
        if menu.opcode == menu_opcode:
            return menu.fields[field][0]
    return None


def nblk(blocks: Blocks, block: Block) -> Prototype | None:
    if prototype := nblocks.get(block.opcode):
        return prototype
    # Motion
    if block.opcode == "motion_goto":
        match getmenu(blocks, block, "TO", "motion_goto_menu"):
            case "_mouse_":
                return Prototype("goto_mouse_pointer", [])
            case "_random_":
                return Prototype("goto_random_position", [])
            case _:
                return Prototype("goto", ["TO"])
    if block.opcode == "motion_glideto":
        # match blocks.blocks[block.inputs.TO[1]].fields.TO[0]:
        match getmenu(blocks, block, "TO", "motion_glideto_menu"):
            case "_mouse_":
                return Prototype("glide_to_mouse_pointer", ["SECS"])
            case "_random_":
                return Prototype("glide_to_random_position", ["SECS"])
            case _:
                return Prototype("glide", ["TO", "SECS"])
    if block.opcode == "motion_pointtowards":
        # match blocks.blocks[block.inputs.TOWARDS[1]].fields.TOWARDS[0]:
        match getmenu(blocks, block, "TOWARDS", "motion_pointtowards_menu"):
            case "_mouse_":
                return Prototype("point_towards_mouse_pointer", [])
            case "_random_":
                return Prototype("point_towards_random_direction", [])
            case _:
                return Prototype("point_towards", ["TOWARDS"])
    if block.opcode == "motion_setrotationstyle":
        match block.fields.STYLE[0]:
            case "left-right":
                return Prototype("set_rotation_style_left_right", [])
            case "don't rotate":
                return Prototype("set_rotation_style_do_not_rotate", [])
            case "all around":
                return Prototype("set_rotation_style_all_around", [])
    # Looks
    if block.opcode == "looks_changeeffectby":
        return Prototype(f"change_{block.fields.EFFECT[0].lower()}_effect", ["CHANGE"])
    if block.opcode == "looks_seteffectto":
        return Prototype(f"set_{block.fields.EFFECT[0].lower()}_effect", ["VALUE"])
    if block.opcode == "looks_gotofrontback":
        match block.fields.FRONT_BACK[0]:
            case "front":
                return Prototype("goto_front", [])
            case "back":
                return Prototype("goto_back", [])
    if block.opcode == "looks_goforwardbackwardlayers":
        match block.fields.FORWARD_BACKWARD[0]:
            case "forward":
                return Prototype("go_forward", ["NUM"])
            case "backward":
                return Prototype("go_backward", ["NUM"])
    # TODO: Implement sound blocks
    # Control
    if block.opcode == "control_stop":
        match block.fields.STOP_OPTION[0]:
            case "all":
                return Prototype("stop_all", [])
            case "this script":
                return Prototype("stop_this_script", [])
            case "other scripts in sprite":
                return Prototype("stop_other_scripts", [])
    if block.opcode == "control_create_clone_of":
        match getmenu(blocks, block, "CLONE_OPTION", "control_create_clone_of_menu"):
            case "_myself_":
                return Prototype("clone", [])
            case _:
                return Prototype("clone", ["CLONE_OPTION"])
    # Sensing
    if block.opcode == "sensing_setdragmode":
        match block.fields.DRAG_MODE[0]:
            case "draggable":
                return Prototype("set_drag_mode_draggable", [])
            case "not draggable":
                return Prototype("set_drag_mode_not_draggable", [])
    # Pen
    if (
        block.opcode == "pen_setPenColorParamTo"
        or block.opcode == "pen_changePenColorParamBy"
    ):
        method = "set" if block.opcode == "pen_setPenColorParamTo" else "change"
        COLOR_PARAM = block.inputs.COLOR_PARAM
        if COLOR_PARAM[0] == 1:
            color_param_menu = blocks.blocks[COLOR_PARAM[1]]
            if color_param_menu.opcode == "pen_menu_colorParam":
                param = color_param_menu.fields.colorParam[0].replace("color", "hue")
                return Prototype(f"{method}_pen_{param}", ["VALUE"])
            raise NotImplementedError(block)


nreporters = {
    # Motion
    "motion_xposition": Prototype("x_position", []),
    "motion_yposition": Prototype("y_position", []),
    "motion_direction": Prototype("direction", []),
    # Looks
    "looks_size": Prototype("size", []),
    # Sound
    "sound_volume": Prototype("volume", []),
    # Sensing
    "sensing_mousedown": Prototype("mouse_down", []),
    "sensing_mousex": Prototype("mouse_x", []),
    "sensing_mousey": Prototype("mouse_y", []),
    "sensing_loudness": Prototype("loudness", []),
    "sensing_timer": Prototype("timer", []),
    "sensing_dayssince2000": Prototype("days_since_2000", []),
    "sensing_username": Prototype("username", []),
    "sensing_touchingcolor": Prototype("touching_color", ["COLOR"]),
    "sensing_coloristouchingcolor": Prototype(
        "color_is_touching_color", ["COLOR", "COLOR2"]
    ),
    "sensing_answer": Prototype("answer", []),
    "sensing_keypressed": Prototype("key_pressed", ["KEY_OPTION"]),
    # Operators
    "operator_random": Prototype("random", ["FROM", "TO"]),
    "operator_contains": Prototype("contains", ["STRING1", "STRING2"]),
    "operator_length": Prototype("length", ["STRING"]),
    "operator_round": Prototype("round", ["NUM"]),
}


def nblkreporter(blocks: Blocks, block: Block) -> Prototype | None:
    if prototype := nreporters.get(block.opcode):
        return prototype
    # Looks
    if block.opcode == "looks_costumenumbername":
        return Prototype(f"costume_{block.fields.NUMBER_NAME[0]}", [])
    if block.opcode == "looks_backdropnumbername":
        return Prototype(f"backdrop_{block.fields.NUMBER_NAME[0]}", [])
    # Sensing
    if block.opcode == "sensing_distanceto":
        match getmenu(blocks, block, "DISTANCETOMENU", "sensing_distancetomenu"):
            case "_mouse_":
                return Prototype("distance_to_mouse_pointer", [])
            case _:
                return Prototype("distance_to", ["DISTANCETOMENU"])
    if block.opcode == "sensing_touchingobject":
        match getmenu(
            blocks, block, "TOUCHINGOBJECTMENU", "sensing_touchingobjectmenu"
        ):
            case "_mouse_":
                return Prototype("touching_mouse_pointer", [])
            case "_edge_":
                return Prototype("touching_edge", [])
            case _:
                return Prototype("touching", ["TOUCHINGOBJECTMENU"])
    if block.opcode == "sensing_current":
        return Prototype(
            f"current_{block.fields.CURRENTMENU[0].lower().replace('dayofweek', 'day_of_week')}",
            [],
        )
    # Operators
    if block.opcode == "operator_mathop":
        op = block.fields.OPERATOR[0]
        if op == "ceiling":
            op = "ceil"
        if op == "e ^":
            op = "antiln"
        if op == "10 ^":
            op = "antilog"
        return Prototype(op, ["NUM"])
