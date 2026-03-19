import logging
import os

from rich.logging import RichHandler


def setup_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "WARNING"),
        handlers=[RichHandler(enable_link_path=False, log_time_format="")],
        format="%(message)s",
    )
