from __future__ import annotations

import logging
import os

from rich.logging import RichHandler


def setup_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "WARNING"),
        handlers=[RichHandler()],
        format="%(message)s",
    )
