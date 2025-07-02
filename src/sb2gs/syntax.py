from __future__ import annotations

import contextlib
import json
import re

WHITESPACE_RE = re.compile(r"[\s.\-]+")
INVALID_CHARS_RE = re.compile(r"[^a-zA-Z_0-9]")


def identifier(identifier: str) -> str:
    identifier = "_".join(WHITESPACE_RE.split(identifier))
    return INVALID_CHARS_RE.sub("", identifier)


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
