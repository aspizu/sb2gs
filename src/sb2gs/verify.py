from __future__ import annotations

import subprocess
from pathlib import Path

from .errors import Error


def verify(project: Path) -> None:
    exec_path = Path("/usr/bin/goboscript")
    if not exec_path.is_file():
        exec_path = Path("~/.cargo/bin/goboscript").expanduser()
    if not exec_path.is_file():
        exec_path = Path("~/.cargo/bin/goboscript.exe").expanduser()
    if not exec_path.is_file():
        exec_path = Path("C:/Windows/System32/goboscript.exe")
    if not exec_path.is_file():
        msg = "goboscript executable not found. Installation instructions: https://aspizu.github.io/goboscript/install"
        raise Error(msg)
    proc = subprocess.run(  # noqa: S603
        [exec_path.as_posix(), "build", "-i", project.as_posix()], check=False
    )
    if proc.returncode != 0:
        msg = "goboscript verification failed. The decompiled code is not valid."
        raise Error(msg)
