from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from .syntax import create_number, create_string

if TYPE_CHECKING:
    from .decompile_sprite import Ctx


def decompile_value(ctx: Ctx, value: object, type: type | None = None) -> None:
    if type is not None:
        with contextlib.suppress(ValueError):
            value = type(value)
    if isinstance(value, bool):
        ctx.print('"true"' if value else '"false"')
        return
    if isinstance(value, (int, float)):
        ctx.print(create_number(value))
        return
    if isinstance(value, str):
        ctx.print(create_string(value))
        return
    msg = f"Unsupported value {value!r}"
    raise ValueError(msg)


def decompile_stack(ctx: Ctx, next: str | None) -> None:
    from .decompile_stmt import decompile_stmt

    if next is None:
        ctx.println("{}")
        return
    ctx.println("{")
    with ctx.indent():
        decompile_stmt(ctx, ctx.blocks[next])
    ctx.println("}")
