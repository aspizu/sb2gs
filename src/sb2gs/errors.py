from __future__ import annotations

from typing import override


class Error(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__()
        self.msg: str = msg

    @override
    def __str__(self) -> str:
        return self.msg
