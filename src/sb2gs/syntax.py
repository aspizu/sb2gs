from __future__ import annotations

import contextlib
import functools
import itertools
import json
import logging
import re

WHITESPACE_RE = re.compile(r"[\s.\-]+")
INVALID_CHARS_RE = re.compile(r"[^a-zA-Z_0-9]")

KEYWORDS = {
    "costumes",
    "sounds",
    "local",
    "proc",
    "func",
    "return",
    "nowarp",
    "on",
    "onflag",
    "onkey",
    "onclick",
    "onbackdrop",
    "onloudness",
    "ontimer",
    "onclone",
    "if",
    "else",
    "elif",
    "until",
    "forever",
    "repeat",
    "not",
    "and",
    "or",
    "in",
    "length",
    "round",
    "abs",
    "floor",
    "ceil",
    "sqrt",
    "sin",
    "cos",
    "tan",
    "asin",
    "acos",
    "atan",
    "ln",
    "log",
    "antiln",
    "antilog",
    "show",
    "hide",
    "add",
    "to",
    "delete",
    "insert",
    "at",
    "of",
    "as",
    "enum",
    "struct",
    "true",
    "false",
    "list",
    "cloud",
    "set_x",
    "set_y",
    "set_size",
    "point_in_direction",
    "set_volume",
    "set_rotation_style_left_right",
    "set_rotation_style_all_around",
    "set_rotation_style_do_not_rotate",
    "set_layer_order",
    "var",
}
identifier_map: dict[str, str] = {}


@functools.cache
def get_blocknames() -> set[str]:
    from . import decompile_expr, decompile_stmt

    all_signatures = itertools.chain(
        decompile_stmt.BLOCKS.values(),
        decompile_expr.BLOCKS.values(),
    )
    blocknames = set()
    for s in all_signatures:
        blocknames.add(s.opcode)
        if s.overloads:
            for overload in s.overloads.values():
                blocknames.add(overload)
    return blocknames


def identifier(og: str) -> str:
    if og in identifier_map:
        return identifier_map[og]

    iden = og

    iden = "_".join(WHITESPACE_RE.split(iden))
    iden = INVALID_CHARS_RE.sub("", iden)

    # remove ugly leading and trailing underscores, and convert to lowercase
    # (in most cases, this converts to snake case)
    # any concerns with naming conflicts are solved at the end of the script, by appending a number
    iden = iden.strip('_').lower()

    if iden in KEYWORDS or iden in get_blocknames():
        iden += "_"

    # any still invalid names can be solved by adding an underscore. e.g. '' -> '_', or '2swap' -> '_2swap'
    if iden == '' or iden[0] in "0123456789":
        iden = '_' + iden

    i = 2 # identifier_1 would be the original one, i.e. #1, so it doesnt need an index.
    new_iden = iden
    while new_iden in identifier_map.values():
        new_iden = f"{iden}{i}"
        i += 1

    identifier_map[og] = new_iden
    logging.info(f"Mapped identifier {og!r} -> {new_iden!r}")

    return new_iden


def string(text: str) -> str:
    return json.dumps(text)


def number(value: float) -> str:
    return json.dumps(value)


def is_goboscript_literal(text: str) -> bool:
    with contextlib.suppress(json.JSONDecodeError):
        parsed = json.loads(text)
        return type(parsed) in {int, float} and json.dumps(parsed) == text
    return False


def value(text: str) -> str:
    if is_goboscript_literal(text):
        return text
    return string(text)
