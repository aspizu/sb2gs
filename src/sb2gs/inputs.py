from __future__ import annotations

from typing import Any


def block_id(input: list[Any] | None) -> str | None:
    if input is None:
        return None
    if isinstance(input[1], str):
        return input[1]
    return None
