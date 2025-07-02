from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._types import Block

PROCCODE_ARG_RE = re.compile(r"\%[sb]")


def get_name(block: Block) -> str:
    return PROCCODE_ARG_RE.sub("", block.mutation.proccode).strip()
