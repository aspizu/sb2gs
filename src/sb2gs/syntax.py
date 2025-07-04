from __future__ import annotations

import contextlib
import json
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


def identifier(identifier: str) -> str:
    identifier = "_".join(WHITESPACE_RE.split(identifier))
    identifier = INVALID_CHARS_RE.sub("", identifier)
    if identifier in KEYWORDS:
        identifier += "_"
    return identifier


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
