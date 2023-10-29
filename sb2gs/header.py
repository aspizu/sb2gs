from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from importlib.resources import files

from . import res


@dataclass
class Prototype:
    name: str
    inputs: list[str]
    defaultinput: tuple[str, str] | None = None
    defaultfield: tuple[str, str] | None = None


def load_header(name: str):
    blocks: dict[str, list[Prototype]] = defaultdict(list)
    file = (files(res) / name).open(newline="")

    for line in file:
        line = line.strip()
        if line.startswith("#"):
            continue
        name, _inputs, _opcode = (i.strip() for i in line.split("|"))
        name = name.removesuffix("?")
        inputs = [i.strip() for i in _inputs.split(",")] if _inputs != "" else []

        if "!" in _opcode:
            opcode, _input = _opcode.split("!")
            input, value = _input.split("=")
            blocks[opcode].append(Prototype(name, inputs, defaultinput=(input, value)))
        elif "." in _opcode:
            opcode, _field = _opcode.split(".")
            field, value = _field.split("=")
            blocks[opcode].append(Prototype(name, inputs, defaultfield=(field, value)))
        else:
            opcode = _opcode
            blocks[opcode].append(Prototype(name, inputs))
    return blocks


STATEMENTS = load_header("statements.txt")
REPORTERS = load_header("reporters.txt")
