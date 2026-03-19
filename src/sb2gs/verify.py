import logging
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

goboscript = shutil.which("goboscript")


def verify(project: Path) -> None:
    if not goboscript:
        logger.error(
            "goboscript executable not found. Installation instructions: https://aspiz.uk/goboscript/docs/install.html"
        )
        sys.exit(1)
    proc = subprocess.run(  # noqa: S603
        [goboscript, "b", project], check=False
    )
    if proc.returncode != 0:
        logger.error("goboscript failed to compile the decompiled code.")
        sys.exit(1)
