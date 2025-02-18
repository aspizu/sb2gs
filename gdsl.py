from dataclasses import dataclass
from typing import Literal


@dataclass
class UnOp:
    opcode: str
    input: str
    fields: dict[str, str]


@dataclass
class BinOp:
    opcode: str
    lhs: str
    rhs: str


@dataclass
class Menu:
    input: str
    field: str
    opcode: str
    default: str


@dataclass
class Block:
    name: str
    opcode: str
    args: list[str]
    fields: dict[str, str]
    menu: Menu | None


def snake_to_pascal(s: str):
    return "".join(x.title() for x in s.split("_"))


def table_split(table: str, n: int):
    xs = table.split()
    xs.extend([""] * (n - len(xs)))
    return xs


def parse():
    un_ops: dict[str, UnOp | None] = {}
    bin_ops: dict[str, BinOp | None] = {}
    blocks: dict[str, Block | list[Block]] = {}
    reporters: dict[str, Block | list[Block]] = {}
    old_opcode = ""
    old_input = ""
    old_lhs = ""
    old_rhs = ""
    old_fields: list[str] = []
    old_menu = ""
    opcode_prefix = ""
    old_args = ""
    section: Literal["UNARY", "BINARY", "BLOCKS", "REPORTERS"] | None = None
    lines = iter(open("gdsl.txt"))
    for line in lines:
        line = line[:-1].strip()
        if line.startswith("#") or not line:
            continue
        print(line)
        if line in ["UNARY OPERATORS", "BINARY OPERATORS", "BLOCKS", "REPORTERS"]:
            section = line.split()[0]  # type: ignore
            next(lines, None)
            next(lines, None)
            next(lines, None)
            continue
        if section == "UNARY":
            if line.endswith("~"):
                un_ops[line.removesuffix("~")] = None
                continue
            table, fields = line.split("|")
            fields = fields.strip()
            fields = (
                dict(
                    (old_fields[i] if key == "..." else key, value)
                    for i, (key, value) in enumerate(
                        x.split("=") for x in fields.strip().split(",")
                    )
                )
                if fields
                else {}
            )
            old_fields = list(fields.keys())
            variant, opcode, input = table.split()
            if opcode == "...":
                opcode = old_opcode
            else:
                opcode = "operator_" + opcode
                old_opcode = opcode
            if input == "...":
                input = old_input
            else:
                old_input = input
            un_ops[variant] = UnOp(opcode, input, fields)
        elif section == "BINARY":
            if line.endswith("~"):
                bin_ops[line.removesuffix("~")] = None
                continue
            variant, opcode, lhs, rhs = line.split()
            if opcode == "...":
                opcode = old_opcode
            else:
                opcode = "operator_" + opcode
                old_opcode = opcode
            if lhs == "...":
                lhs = old_lhs
            else:
                old_lhs = lhs
            if rhs == "...":
                rhs = old_rhs
            else:
                old_rhs = rhs
            bin_ops[variant] = BinOp(opcode, lhs, rhs)
        else:
            if line.startswith("["):
                opcode_prefix = line.split("]")[0].removeprefix("[")
                continue
            table, fields, menu = line.split("|")
            menu = menu.strip()
            if menu:
                input_opcode, default = menu.split("=")
                if input_opcode == "...":
                    input_opcode = old_menu
                old_menu = input_opcode
                input, opcode = input_opcode.split(":")
                if "@" in input:
                    input, field = input.split("@")
                else:
                    field = input
                menu = Menu(
                    input=input,
                    field=field,
                    opcode=opcode,
                    default=default,
                )
            else:
                menu = None
            fields = fields.strip()
            fields = (
                dict(
                    (old_fields[i] if key == "..." else key, value)
                    for i, (key, value) in enumerate(
                        x.split("=") for x in fields.strip().split(",")
                    )
                )
                if fields
                else {}
            )
            old_fields = list(fields.keys())
            name, opcode, args = table_split(table, 3)
            variant = snake_to_pascal(name)
            if opcode == "...":
                opcode = old_opcode
            else:
                old_opcode = opcode
            opcode = f"{opcode_prefix}_{opcode}"
            if args == "...":
                args = old_args
            else:
                old_args = args
            args = args.split(",") if args else []
            if section == "BLOCKS":
                container = blocks
            else:
                container = reporters
            if variant in container:
                block = container[variant]
                if not isinstance(block, list):
                    block = [block]
                block.append(Block(name, opcode, args, fields, menu))
                container[variant] = block
            else:
                container[variant] = Block(name, opcode, args, fields, menu)
    return un_ops, bin_ops, blocks, reporters


un_ops, bin_ops, blocks, reporters = parse()

f = open("src/sb2gs/blocks.py", "w")
f.write("""
from dataclasses import dataclass


@dataclass
class UnOp:
    opcode: str
    input: str
    fields: dict[str, str]


@dataclass
class BinOp:
    opcode: str
    lhs: str
    rhs: str


@dataclass
class Menu:
    input: str
    field: str
    opcode: str
    default: str


@dataclass
class Block:
    name: str
    opcode: str
    args: list[str]
    fields: dict[str, str]
    menu: Menu | None
""")
f.write("blocks: list[Block|list[Block]] = [\n")
for block in blocks.values():
    f.write(repr(block) + ",\n")
f.write("]\n")
f.write("reporters: list[Block|list[Block]] = [\n")
for block in reporters.values():
    f.write(repr(block) + ",\n")
f.write("]\n")
f.write("un_ops = [\n")
for block in un_ops.values():
    f.write(repr(block) + ",\n")
f.write("]\n")
f.write("bin_ops = [\n")
for block in bin_ops.values():
    f.write(repr(block) + ",\n")
f.write("]\n")
