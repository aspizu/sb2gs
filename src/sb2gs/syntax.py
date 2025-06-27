from __future__ import annotations

import json
import re

WHITESPACE_RE = re.compile(r"[\s.\-]+")
INVALID_CHARS_RE = re.compile(r"[^a-zA-Z_0-9]")


def create_identifier(identifier: str) -> str:
    identifier = "_".join(WHITESPACE_RE.split(identifier))
    return INVALID_CHARS_RE.sub("", identifier)


def create_string(string: str) -> str:
    return json.dumps(string)


def create_number(number: float) -> str:
    if int(number) == number:
        return str(int(number))
    return str(number)
