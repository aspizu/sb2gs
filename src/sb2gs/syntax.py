from __future__ import annotations

import contextlib
import json
import math
import re

WHITESPACE_RE = re.compile(r"[\s.\-]+")
INVALID_CHARS_RE = re.compile(r"[^a-zA-Z_0-9]")


def identifier(identifier: str) -> str:
    identifier = "_".join(WHITESPACE_RE.split(identifier))
    return INVALID_CHARS_RE.sub("", identifier)


def string(text: str) -> str:
    return json.dumps(text)


def number(num: float) -> str:
    if math.isinf(num) and num > 0:
        return string("Infinity")
    if math.isinf(num) and num < 0:
        return string("-Infinity")
    if math.isnan(num):
        return string("NaN")
    if num.is_integer():
        return str(int(num))
    return str(num)


def value(text: str) -> str:
    with contextlib.suppress(ValueError):
        value = float(text)
        result = number(value)
        if text == result and math.isfinite(value):
            return result
    return string(text)
