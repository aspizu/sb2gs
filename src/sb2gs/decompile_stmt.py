from __future__ import annotations

from typing import TYPE_CHECKING

from rich import print

from . import inputs
from .decompile_input import decompile_input

if TYPE_CHECKING:
    from .decompile_sprite import Ctx
    from .types import Block

BLOCKS = {
    # Motion
    "motion_movesteps": ("move", ["STEPS"]),
    "motion_turnleft": ("turn_left", ["DEGREES"]),
    "motion_turnright": ("turn_right", ["DEGREES"]),
    "motion_gotoxy": ("goto", ["X", "Y"]),
    "motion_glidesecstoxy": ("glide", ["X", "Y", "SECS"]),
    "motion_pointindirection": ("point_in_direction", ["DIRECTION"]),
    "motion_changexby": ("change_x", ["DX"]),
    "motion_setx": ("set_x", ["X"]),
    "motion_changeyby": ("change_y", ["DY"]),
    "motion_sety": ("set_y", ["Y"]),
    "motion_ifonedgebounce": ("if_on_edge_bounce", []),
    # Looks
    "looks_sayforsecs": ("say", ["MESSAGE", "SECS"]),
    "looks_thinkforsecs": ("think", ["MESSAGE", "SECS"]),
    "looks_say": ("say", ["MESSAGE"]),
    "looks_think": ("think", ["MESSAGE"]),
    "looks_switchcostumeto": ("switch_costume", ["COSTUME"]),
    "looks_nextcostume": ("next_costume", []),
    "looks_nextbackdrop": ("next_backdrop", []),
    "looks_setsizeto": ("set_size", ["SIZE"]),
    "looks_changesizeby": ("change_size", ["CHANGE"]),
    "looks_cleargraphiceffects": ("clear_graphic_effects", []),
    "looks_show": ("show", []),
    "looks_hide": ("hide", []),
    # Sound
    "sound_playuntildone": ("play_sound_until_done", ["SOUND_MENU"]),
    "sound_play": ("start_sound", ["SOUND_MENU"]),
    "sound_stopallsounds": ("stop_all_sounds", []),
    "sound_changevolumeby": ("change_volume", ["VOLUME"]),
    "sound_setvolumeto": ("set_volume", ["VOLUME"]),
    "sound_cleareffects": ("clear_sound_effects", []),
    # Event
    "event_broadcast": ("broadcast", ["BROADCAST_INPUT"]),
    "event_broadcastandwait": ("broadcast_and_wait", ["BROADCAST_INPUT"]),
    # Control
    "control_wait": ("wait", ["DURATION"]),
    "control_delete_this_clone": ("delete_this_clone", []),
    # Sensing
    "sensing_askandwait": ("ask", ["QUESTION"]),
    "sensing_resettimer": ("reset_timer", []),
    # Pen
    "pen_clear": ("erase_all", []),
    "pen_stamp": ("stamp", []),
    "pen_penDown": ("pen_down", []),
    "pen_penUp": ("pen_up", []),
    "pen_setPenColorToColor": ("set_pen_color", ["COLOR"]),
    "pen_changePenSizeBy": ("change_pen_size", ["SIZE"]),
    "pen_setPenSizeTo": ("set_pen_size", ["SIZE"]),
    # Music
    "music_restForBeats": ("rest", ["BEATS"]),
    "music_setTempo": ("set_tempo", ["TEMPO"]),
    "music_changeTempo": ("change_tempo", ["TEMPO"]),
}


def decompile_block(ctx: Ctx, block: Block) -> None:
    opcode, inputs = BLOCKS[block.opcode]
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


def decompile_if(ctx: Ctx, block: Block) -> None:
    from .decompile_code import decompile_stack

    ctx.iprint("if ")
    decompile_input(ctx, "CONDITION", block)
    ctx.print(" ")
    decompile_stack(ctx, inputs.block_id(block.inputs._.get("SUBSTACK")))
    decompile_else(ctx, inputs.block_id(block.inputs._.get("SUBSTACK2")))


def decompile_stmt(ctx: Ctx, block: Block) -> None:
    print(block)
    if block.opcode in BLOCKS:
        decompile_block(ctx, block)
        return
    if block.opcode.startswith("control_if"):
        decompile_if(ctx, block)
        return
