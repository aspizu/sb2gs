from dataclasses import dataclass


@dataclass
class UnOp:
    opcode: str
    input: str
    fields: dict[str, str]


@dataclass
class BinOp:
    opcode: str
    lhs: str
    rhs: str


@dataclass
class Menu:
    input: str
    field: str
    opcode: str
    default: str


@dataclass
class Block:
    name: str
    opcode: str
    args: list[str]
    fields: dict[str, str]
    menu: Menu | None


blocks: list[Block | list[Block]] = [
    Block(name="move", opcode="motion_movesteps", args=["STEPS"], fields={}, menu=None),
    Block(
        name="turn_left",
        opcode="motion_turnleft",
        args=["DEGREES"],
        fields={},
        menu=None,
    ),
    Block(
        name="turn_right",
        opcode="motion_turnright",
        args=["DEGREES"],
        fields={},
        menu=None,
    ),
    Block(
        name="goto_random_position",
        opcode="motion_goto",
        args=[],
        fields={},
        menu=Menu(
            input="TO", field="TO", opcode="motion_goto_menu", default="_random_"
        ),
    ),
    Block(
        name="goto_mouse_pointer",
        opcode="motion_goto",
        args=[],
        fields={},
        menu=Menu(input="TO", field="TO", opcode="motion_goto_menu", default="_mouse_"),
    ),
    [
        Block(
            name="goto",
            opcode="motion_goto",
            args=["TO"],
            fields={},
            menu=Menu(
                input="TO", field="TO", opcode="motion_goto_menu", default="_random_"
            ),
        ),
        Block(
            name="goto", opcode="motion_gotoxy", args=["X", "Y"], fields={}, menu=None
        ),
    ],
    [
        Block(
            name="glide",
            opcode="motion_glidesecstoxy",
            args=["X", "Y", "SECS"],
            fields={},
            menu=None,
        ),
        Block(
            name="glide",
            opcode="motion_glideto",
            args=["TO", "SECS"],
            fields={},
            menu=Menu(
                input="TO", field="TO", opcode="motion_glideto_menu", default="_random_"
            ),
        ),
    ],
    Block(
        name="glide_to_random_position",
        opcode="motion_glideto",
        args=["SECS"],
        fields={},
        menu=Menu(
            input="TO", field="TO", opcode="motion_glideto_menu", default="_random_"
        ),
    ),
    Block(
        name="glide_to_mouse_pointer",
        opcode="motion_glideto",
        args=["SECS"],
        fields={},
        menu=Menu(
            input="TO", field="TO", opcode="motion_glideto_menu", default="_mouse_"
        ),
    ),
    Block(
        name="point_in_direction",
        opcode="motion_pointindirection",
        args=["DIRECTION"],
        fields={},
        menu=None,
    ),
    Block(
        name="point_towards_mouse_pointer",
        opcode="motion_pointtowards",
        args=[],
        fields={},
        menu=Menu(
            input="TOWARDS",
            field="TOWARDS",
            opcode="motion_pointtowards_menu",
            default="_mouse_",
        ),
    ),
    Block(
        name="point_towards_random_direction",
        opcode="motion_pointtowards",
        args=[],
        fields={},
        menu=Menu(
            input="TOWARDS",
            field="TOWARDS",
            opcode="motion_pointtowards_menu",
            default="_random_",
        ),
    ),
    Block(
        name="point_towards",
        opcode="motion_pointtowards",
        args=["TOWARDS"],
        fields={},
        menu=Menu(
            input="TOWARDS",
            field="TOWARDS",
            opcode="motion_pointtowards_menu",
            default="_random_",
        ),
    ),
    Block(
        name="change_x", opcode="motion_changexby", args=["DX"], fields={}, menu=None
    ),
    Block(name="set_x", opcode="motion_setx", args=["X"], fields={}, menu=None),
    Block(
        name="change_y", opcode="motion_changeyby", args=["DY"], fields={}, menu=None
    ),
    Block(name="set_y", opcode="motion_sety", args=["Y"], fields={}, menu=None),
    Block(
        name="if_on_edge_bounce",
        opcode="motion_ifonedgebounce",
        args=[],
        fields={},
        menu=None,
    ),
    Block(
        name="set_rotation_style_left_right",
        opcode="motion_setrotationstyle",
        args=[],
        fields={"STYLE": "left-right"},
        menu=None,
    ),
    Block(
        name="set_rotation_style_do_not_rotate",
        opcode="motion_setrotationstyle",
        args=[],
        fields={"STYLE": "don't rotate"},
        menu=None,
    ),
    Block(
        name="set_rotation_style_all_around",
        opcode="motion_setrotationstyle",
        args=[],
        fields={"STYLE": "all around"},
        menu=None,
    ),
    [
        Block(
            name="say",
            opcode="looks_sayforsecs",
            args=["MESSAGE", "SECS"],
            fields={},
            menu=None,
        ),
        Block(name="say", opcode="looks_say", args=["MESSAGE"], fields={}, menu=None),
    ],
    [
        Block(
            name="think",
            opcode="looks_thinkforsecs",
            args=["MESSAGE", "SECS"],
            fields={},
            menu=None,
        ),
        Block(
            name="think", opcode="looks_think", args=["MESSAGE"], fields={}, menu=None
        ),
    ],
    Block(
        name="switch_costume",
        opcode="looks_switchcostumeto",
        args=["COSTUME"],
        fields={},
        menu=Menu(
            input="COSTUME",
            field="COSTUME",
            opcode="looks_costume",
            default="make gh issue if this bothers u",
        ),
    ),
    Block(
        name="next_costume", opcode="looks_nextcostume", args=[], fields={}, menu=None
    ),
    Block(
        name="switch_backdrop",
        opcode="looks_switchbackdropto",
        args=["BACKDROP"],
        fields={},
        menu=Menu(
            input="BACKDROP",
            field="BACKDROP",
            opcode="looks_backdrops",
            default="make gh issue if this bothers u",
        ),
    ),
    Block(
        name="next_backdrop", opcode="looks_nextbackdrop", args=[], fields={}, menu=None
    ),
    Block(
        name="set_size", opcode="looks_setsizeto", args=["SIZE"], fields={}, menu=None
    ),
    Block(
        name="change_size",
        opcode="looks_changesizeby",
        args=["CHANGE"],
        fields={},
        menu=None,
    ),
    Block(
        name="change_color_effect",
        opcode="looks_changeeffectby",
        args=["CHANGE"],
        fields={"EFFECT": "COLOR"},
        menu=None,
    ),
    Block(
        name="change_fisheye_effect",
        opcode="looks_changeeffectby",
        args=["CHANGE"],
        fields={"EFFECT": "FISHEYE"},
        menu=None,
    ),
    Block(
        name="change_whirl_effect",
        opcode="looks_changeeffectby",
        args=["CHANGE"],
        fields={"EFFECT": "WHIRL"},
        menu=None,
    ),
    Block(
        name="change_pixelate_effect",
        opcode="looks_changeeffectby",
        args=["CHANGE"],
        fields={"EFFECT": "PIXELATE"},
        menu=None,
    ),
    Block(
        name="change_mosaic_effect",
        opcode="looks_changeeffectby",
        args=["CHANGE"],
        fields={"EFFECT": "MOSAIC"},
        menu=None,
    ),
    Block(
        name="change_brightness_effect",
        opcode="looks_changeeffectby",
        args=["CHANGE"],
        fields={"EFFECT": "BRIGHTNESS"},
        menu=None,
    ),
    Block(
        name="change_ghost_effect",
        opcode="looks_changeeffectby",
        args=["CHANGE"],
        fields={"EFFECT": "GHOST"},
        menu=None,
    ),
    Block(
        name="set_color_effect",
        opcode="looks_seteffectto",
        args=["VALUE"],
        fields={"EFFECT": "COLOR"},
        menu=None,
    ),
    Block(
        name="set_fisheye_effect",
        opcode="looks_seteffectto",
        args=["VALUE"],
        fields={"EFFECT": "FISHEYE"},
        menu=None,
    ),
    Block(
        name="set_whirl_effect",
        opcode="looks_seteffectto",
        args=["VALUE"],
        fields={"EFFECT": "WHIRL"},
        menu=None,
    ),
    Block(
        name="set_pixelate_effect",
        opcode="looks_seteffectto",
        args=["VALUE"],
        fields={"EFFECT": "PIXELATE"},
        menu=None,
    ),
    Block(
        name="set_mosaic_effect",
        opcode="looks_seteffectto",
        args=["VALUE"],
        fields={"EFFECT": "MOSAIC"},
        menu=None,
    ),
    Block(
        name="set_brightness_effect",
        opcode="looks_seteffectto",
        args=["VALUE"],
        fields={"EFFECT": "BRIGHTNESS"},
        menu=None,
    ),
    Block(
        name="set_ghost_effect",
        opcode="looks_seteffectto",
        args=["VALUE"],
        fields={"EFFECT": "GHOST"},
        menu=None,
    ),
    Block(
        name="clear_graphic_effects",
        opcode="looks_cleargraphiceffects",
        args=[],
        fields={},
        menu=None,
    ),
    Block(name="show", opcode="looks_show", args=[], fields={}, menu=None),
    Block(name="hide", opcode="looks_hide", args=[], fields={}, menu=None),
    Block(
        name="goto_front",
        opcode="looks_gotofrontback",
        args=[],
        fields={"FRONT_BACK": "front"},
        menu=None,
    ),
    Block(
        name="goto_back",
        opcode="looks_gotofrontback",
        args=[],
        fields={"FRONT_BACK": "back"},
        menu=None,
    ),
    Block(
        name="go_forward",
        opcode="looks_goforwardbackwardlayers",
        args=["NUM"],
        fields={"FORWARD_BACKWARD": "forward"},
        menu=None,
    ),
    Block(
        name="go_backward",
        opcode="looks_goforwardbackwardlayers",
        args=["NUM"],
        fields={"FORWARD_BACKWARD": "backward"},
        menu=None,
    ),
    Block(
        name="play_sound_until_done",
        opcode="sound_playuntildone",
        args=["SOUND_MENU"],
        fields={},
        menu=Menu(
            input="SOUND_MENU",
            field="SOUND_MENU",
            opcode="sound_sounds_menu",
            default="make gh issue if this bothers u",
        ),
    ),
    Block(
        name="start_sound",
        opcode="sound_play",
        args=["SOUND_MENU"],
        fields={},
        menu=Menu(
            input="SOUND_MENU",
            field="SOUND_MENU",
            opcode="sound_sounds_menu",
            default="make gh issue if this bothers u",
        ),
    ),
    Block(
        name="stop_all_sounds",
        opcode="sound_stopallsounds",
        args=[],
        fields={},
        menu=None,
    ),
    Block(
        name="change_pitch_effect",
        opcode="sound_changeeffectby",
        args=["VALUE"],
        fields={"EFFECT": "PITCH"},
        menu=None,
    ),
    Block(
        name="change_pan_effect",
        opcode="sound_changeeffectby",
        args=["VALUE"],
        fields={"EFFECT": "PAN"},
        menu=None,
    ),
    Block(
        name="set_pitch_effect",
        opcode="sound_seteffectto",
        args=["VALUE"],
        fields={"EFFECT": "PITCH"},
        menu=None,
    ),
    Block(
        name="set_pan_effect",
        opcode="sound_seteffectto",
        args=["VALUE"],
        fields={"EFFECT": "PAN"},
        menu=None,
    ),
    Block(
        name="change_volume",
        opcode="sound_changevolumeby",
        args=["VOLUME"],
        fields={},
        menu=None,
    ),
    Block(
        name="set_volume",
        opcode="sound_setvolumeto",
        args=["VOLUME"],
        fields={},
        menu=None,
    ),
    Block(
        name="clear_sound_effects",
        opcode="sound_cleareffects",
        args=[],
        fields={},
        menu=None,
    ),
    Block(
        name="broadcast",
        opcode="event_broadcast",
        args=["BROADCAST_INPUT"],
        fields={},
        menu=None,
    ),
    Block(
        name="broadcast_and_wait",
        opcode="event_broadcastandwait",
        args=["BROADCAST_INPUT"],
        fields={},
        menu=None,
    ),
    Block(name="wait", opcode="control_wait", args=["DURATION"], fields={}, menu=None),
    Block(
        name="wait_until",
        opcode="control_wait_until",
        args=["CONDITION"],
        fields={},
        menu=None,
    ),
    Block(
        name="stop_all",
        opcode="control_stop",
        args=[],
        fields={"STOP_OPTION": "all"},
        menu=None,
    ),
    Block(
        name="stop_this_script",
        opcode="control_stop",
        args=[],
        fields={"STOP_OPTION": "this script"},
        menu=None,
    ),
    Block(
        name="stop_other_scripts",
        opcode="control_stop",
        args=[],
        fields={"STOP_OPTION": "other scripts in sprite"},
        menu=None,
    ),
    Block(
        name="delete_this_clone",
        opcode="control_delete_this_clone",
        args=[],
        fields={},
        menu=None,
    ),
    [
        Block(
            name="clone",
            opcode="control_create_clone_of",
            args=[],
            fields={},
            menu=Menu(
                input="CLONE_OPTION",
                field="CLONE_OPTION",
                opcode="control_create_clone_of_menu",
                default="_myself_",
            ),
        ),
        Block(
            name="clone",
            opcode="control_create_clone_of",
            args=["CLONE_OPTION"],
            fields={},
            menu=Menu(
                input="CLONE_OPTION",
                field="CLONE_OPTION",
                opcode="control_create_clone_of_menu",
                default="_myself_",
            ),
        ),
    ],
    Block(
        name="ask", opcode="sensing_askandwait", args=["QUESTION"], fields={}, menu=None
    ),
    Block(
        name="set_drag_mode_draggable",
        opcode="sensing_setdragmode",
        args=[],
        fields={"DRAG_MODE": "draggable"},
        menu=None,
    ),
    Block(
        name="set_drag_mode_not_draggable",
        opcode="sensing_setdragmode",
        args=[],
        fields={"DRAG_MODE": "not draggable"},
        menu=None,
    ),
    Block(
        name="reset_timer", opcode="sensing_resettimer", args=[], fields={}, menu=None
    ),
    Block(name="erase_all", opcode="pen_clear", args=[], fields={}, menu=None),
    Block(name="stamp", opcode="pen_stamp", args=[], fields={}, menu=None),
    Block(name="pen_down", opcode="pen_penDown", args=[], fields={}, menu=None),
    Block(name="pen_up", opcode="pen_penUp", args=[], fields={}, menu=None),
    Block(
        name="set_pen_color",
        opcode="pen_setPenColorToColor",
        args=["COLOR"],
        fields={},
        menu=None,
    ),
    Block(
        name="change_pen_size",
        opcode="pen_changePenSizeBy",
        args=["SIZE"],
        fields={},
        menu=None,
    ),
    Block(
        name="set_pen_size",
        opcode="pen_setPenSizeTo",
        args=["SIZE"],
        fields={},
        menu=None,
    ),
    Block(
        name="set_pen_hue",
        opcode="pen_setPenColorParamTo",
        args=["VALUE"],
        fields={},
        menu=Menu(
            input="COLOR_PARAM",
            field="colorParam",
            opcode="pen_menu_colorParam",
            default="color",
        ),
    ),
    Block(
        name="set_pen_saturation",
        opcode="pen_setPenColorParamTo",
        args=["VALUE"],
        fields={},
        menu=Menu(
            input="COLOR_PARAM",
            field="colorParam",
            opcode="pen_menu_colorParam",
            default="saturation",
        ),
    ),
    Block(
        name="set_pen_brightness",
        opcode="pen_setPenColorParamTo",
        args=["VALUE"],
        fields={},
        menu=Menu(
            input="COLOR_PARAM",
            field="colorParam",
            opcode="pen_menu_colorParam",
            default="brightness",
        ),
    ),
    Block(
        name="set_pen_transparency",
        opcode="pen_setPenColorParamTo",
        args=["VALUE"],
        fields={},
        menu=Menu(
            input="COLOR_PARAM",
            field="colorParam",
            opcode="pen_menu_colorParam",
            default="transparency",
        ),
    ),
    Block(
        name="change_pen_hue",
        opcode="pen_changePenColorParamBy",
        args=["VALUE"],
        fields={},
        menu=Menu(
            input="COLOR_PARAM",
            field="colorParam",
            opcode="pen_menu_colorParam",
            default="color",
        ),
    ),
    Block(
        name="change_pen_saturation",
        opcode="pen_changePenColorParamBy",
        args=["VALUE"],
        fields={},
        menu=Menu(
            input="COLOR_PARAM",
            field="colorParam",
            opcode="pen_menu_colorParam",
            default="saturation",
        ),
    ),
    Block(
        name="change_pen_brightness",
        opcode="pen_changePenColorParamBy",
        args=["VALUE"],
        fields={},
        menu=Menu(
            input="COLOR_PARAM",
            field="colorParam",
            opcode="pen_menu_colorParam",
            default="brightness",
        ),
    ),
    Block(
        name="change_pen_transparency",
        opcode="pen_changePenColorParamBy",
        args=["VALUE"],
        fields={},
        menu=Menu(
            input="COLOR_PARAM",
            field="colorParam",
            opcode="pen_menu_colorParam",
            default="transparency",
        ),
    ),
    Block(
        name="rest", opcode="music_restForBeats", args=["BEATS"], fields={}, menu=None
    ),
    Block(
        name="set_tempo", opcode="music_setTempo", args=["TEMPO"], fields={}, menu=None
    ),
    Block(
        name="change_tempo",
        opcode="music_changeTempo",
        args=["TEMPO"],
        fields={},
        menu=None,
    ),
]
reporters: list[Block | list[Block]] = [
    Block(name="x_position", opcode="motion_xposition", args=[], fields={}, menu=None),
    Block(name="y_position", opcode="motion_yposition", args=[], fields={}, menu=None),
    Block(name="direction", opcode="motion_direction", args=[], fields={}, menu=None),
    Block(name="size", opcode="looks_size", args=[], fields={}, menu=None),
    Block(
        name="costume_number",
        opcode="looks_costumenumbername",
        args=[],
        fields={"NUMBER_NAME": "number"},
        menu=None,
    ),
    Block(
        name="costume_name",
        opcode="looks_costumenumbername",
        args=[],
        fields={"NUMBER_NAME": "name"},
        menu=None,
    ),
    Block(
        name="backdrop_number",
        opcode="looks_backdropnumbername",
        args=[],
        fields={"NUMBER_NAME": "number"},
        menu=None,
    ),
    Block(
        name="backdrop_name",
        opcode="looks_backdropnumbername",
        args=[],
        fields={"NUMBER_NAME": "name"},
        menu=None,
    ),
    Block(name="volume", opcode="sound_volume", args=[], fields={}, menu=None),
    Block(
        name="distance_to_mouse_pointer",
        opcode="sensing_distanceto",
        args=[],
        fields={},
        menu=Menu(
            input="DISTANCETOMENU",
            field="DISTANCETOMENU",
            opcode="sensing_distancetomenu",
            default="_mouse_",
        ),
    ),
    Block(
        name="distance_to",
        opcode="sensing_distanceto",
        args=["DISTANCETOMENU"],
        fields={},
        menu=Menu(
            input="DISTANCETOMENU",
            field="DISTANCETOMENU",
            opcode="sensing_distancetomenu",
            default="_mouse_",
        ),
    ),
    Block(
        name="touching_mouse_pointer",
        opcode="sensing_touchingobject",
        args=[],
        fields={},
        menu=Menu(
            input="TOUCHINGOBJECTMENU",
            field="TOUCHINGOBJECTMENU",
            opcode="sensing_touchingobjectmenu",
            default="_mouse_",
        ),
    ),
    Block(
        name="touching_edge",
        opcode="sensing_touchingobject",
        args=[],
        fields={},
        menu=Menu(
            input="TOUCHINGOBJECTMENU",
            field="TOUCHINGOBJECTMENU",
            opcode="sensing_touchingobjectmenu",
            default="_edge_",
        ),
    ),
    Block(
        name="touching",
        opcode="sensing_touchingobject",
        args=["TOUCHINGOBJECTMENU"],
        fields={},
        menu=Menu(
            input="TOUCHINGOBJECTMENU",
            field="TOUCHINGOBJECTMENU",
            opcode="sensing_touchingobjectmenu",
            default="_mouse_",
        ),
    ),
    Block(
        name="key_pressed",
        opcode="sensing_keypressed",
        args=["KEY_OPTION"],
        fields={},
        menu=Menu(
            input="KEY_OPTION",
            field="KEY_OPTION",
            opcode="sensing_keyoptions",
            default="any",
        ),
    ),
    Block(name="mouse_down", opcode="sensing_mousedown", args=[], fields={}, menu=None),
    Block(name="mouse_x", opcode="sensing_mousex", args=[], fields={}, menu=None),
    Block(name="mouse_y", opcode="sensing_mousey", args=[], fields={}, menu=None),
    Block(name="loudness", opcode="sensing_loudness", args=[], fields={}, menu=None),
    Block(name="timer", opcode="sensing_timer", args=[], fields={}, menu=None),
    Block(
        name="current_year",
        opcode="sensing_current",
        args=[],
        fields={"CURRENTMENU": "YEAR"},
        menu=None,
    ),
    Block(
        name="current_month",
        opcode="sensing_current",
        args=[],
        fields={"CURRENTMENU": "MONTH"},
        menu=None,
    ),
    Block(
        name="current_date",
        opcode="sensing_current",
        args=[],
        fields={"CURRENTMENU": "DATE"},
        menu=None,
    ),
    Block(
        name="current_day_of_week",
        opcode="sensing_current",
        args=[],
        fields={"CURRENTMENU": "DAYOFWEEK"},
        menu=None,
    ),
    Block(
        name="current_hour",
        opcode="sensing_current",
        args=[],
        fields={"CURRENTMENU": "HOUR"},
        menu=None,
    ),
    Block(
        name="current_minute",
        opcode="sensing_current",
        args=[],
        fields={"CURRENTMENU": "MINUTE"},
        menu=None,
    ),
    Block(
        name="current_second",
        opcode="sensing_current",
        args=[],
        fields={"CURRENTMENU": "SECOND"},
        menu=None,
    ),
    Block(
        name="days_since_2000",
        opcode="sensing_dayssince2000",
        args=[],
        fields={},
        menu=None,
    ),
    Block(name="username", opcode="sensing_username", args=[], fields={}, menu=None),
    Block(
        name="touching_color",
        opcode="sensing_touchingcolor",
        args=["COLOR"],
        fields={},
        menu=None,
    ),
    Block(
        name="color_is_touching_color",
        opcode="sensing_coloristouchingcolor",
        args=["COLOR", "COLOR2"],
        fields={},
        menu=None,
    ),
    Block(name="answer", opcode="sensing_answer", args=[], fields={}, menu=None),
    Block(
        name="random",
        opcode="operator_random",
        args=["FROM", "TO"],
        fields={},
        menu=None,
    ),
    Block(
        name="contains",
        opcode="operator_contains",
        args=["STRING1", "STRING2"],
        fields={},
        menu=None,
    ),
]
un_ops = [
    UnOp(opcode="operator_not", input="OPERAND", fields={}),
    UnOp(opcode="operator_length", input="STRING", fields={}),
    UnOp(opcode="operator_round", input="NUM", fields={}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "abs"}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "floor"}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "ceiling"}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "sqrt"}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "sin"}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "cos"}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "tan"}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "asin"}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "acos"}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "atan"}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "ln"}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "log"}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "e ^"}),
    UnOp(opcode="operator_mathop", input="NUM", fields={"OPERATOR": "10 ^"}),
    None,
]
bin_ops = [
    BinOp(opcode="operator_add", lhs="NUM1", rhs="NUM2"),
    BinOp(opcode="operator_subtract", lhs="NUM1", rhs="NUM2"),
    BinOp(opcode="operator_multiply", lhs="NUM1", rhs="NUM2"),
    BinOp(opcode="operator_divide", lhs="NUM1", rhs="NUM2"),
    BinOp(opcode="operator_mod", lhs="NUM1", rhs="NUM2"),
    BinOp(opcode="operator_lt", lhs="OPERAND1", rhs="OPERAND2"),
    BinOp(opcode="operator_gt", lhs="OPERAND1", rhs="OPERAND2"),
    BinOp(opcode="operator_equals", lhs="OPERAND1", rhs="OPERAND2"),
    BinOp(opcode="operator_and", lhs="OPERAND1", rhs="OPERAND2"),
    BinOp(opcode="operator_or", lhs="OPERAND1", rhs="OPERAND2"),
    BinOp(opcode="operator_join", lhs="STRING1", rhs="STRING2"),
    BinOp(opcode="operator_contains", lhs="STRING2", rhs="STRING1"),
    BinOp(opcode="operator_letter_of", lhs="STRING", rhs="LETTER"),
    None,
    None,
    None,
    None,
]
