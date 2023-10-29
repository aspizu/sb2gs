from __future__ import annotations

import contextlib
import json
import string
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TextIO

from rich import print

from .header import REPORTERS, STATEMENTS, Prototype
from .sb3 import Input, Target

if TYPE_CHECKING:
    from .sb3 import Block, Namespace


def get_name(name: str):
    name = "_".join(name.split())
    return "".join(i for i in name if i in string.ascii_letters + string.digits + "_")


@dataclass
class BinaryOperator:
    opcode: str
    syntax: str
    precedence: int
    left: str
    right: str


class Blocks:
    # fmt: off
    OPERATORS = { k: BinaryOperator(k, *v) for k, v in {
    #   OPCODE           : SYNTAX | PRECEDENCE | LEFT       | RIGHT       #
    #--------------------:--------|------------|------------|-------------#
    "operator_and"       :( "and" ,-1          , "OPERAND1" , "OPERAND2" ),
    "operator_or"        :( "or"  ,-1          , "OPERAND1" , "OPERAND2" ),
    "operator_not"       :( "not" , 0          , "OPERAND"  , ""         ),
    "operator_contains"  :( "in"  , 0          , "STRING2"  , "STRING1"  ),
    "operator_notequals" :( "!="  , 0          , "OPERAND1" , "OPERAND2" ),
    "operator_equals"    :( "="   , 0          , "OPERAND1" , "OPERAND2" ),
    "operator_lt"        :( "<"   , 0          , "OPERAND1" , "OPERAND2" ),
    "operator_gt"        :( ">"   , 0          , "OPERAND1" , "OPERAND2" ),
    "operator_le"        :( "<="  , 0          , "OPERAND1" , "OPERAND2" ),
    "operator_ge"        :( ">="  , 0          , "OPERAND1" , "OPERAND2" ),
    "operator_join"      :( "&"   , 1          , "STRING1"  , "STRING2"  ),
    "operator_add"       :( "+"   , 1          , "NUM1"     , "NUM2"     ),
    "operator_subtract"  :( "-"   , 1          , "NUM1"     , "NUM2"     ),
    "operator_multiply"  :( "*"   , 2          , "NUM1"     , "NUM2"     ),
    "operator_divide"    :( "/"   , 2          , "NUM1"     , "NUM2"     ),
    "operator_mod"       :( "%"   , 2          , "NUM1"     , "NUM2"     ),
    "operator_letter_of" :( ""    , 3          , "LETTER"   , "STRING"   ),
    "negative"           :( "-"   , 3          , "NUM1"     , "NUM2"     ),
    }.items()}#-----------------------------------------------------------#
    COMPOUND_OPERATORS = {
    # OPCODE           : SYM #
    #------------------:-----#
    "operator_add"     : "+" ,
    "operator_subtract": "-" ,
    "operator_multiply": "*" ,
    "operator_divide"  : "/" ,
    "operator_mod"     : "%" ,
    #------------------:-----#
    }
    # fmt: on

    def __init__(self, target: Target, file: TextIO):
        self.target = target
        self.blocks = target.blocks
        self.file = file
        self.level = 0

    def write(self, string: str):
        self.file.write(string)

    def tabwrite(self, string: str):
        tab = self.level * "    "
        self.file.write(tab + string)

    def all(self):
        self.tabwrite("costumes ")
        for i, costume in enumerate(self.target.costumes):
            self.value(f"{self.target.name}/{costume.name}.{costume.dataFormat}")
            if i < len(self.target.costumes) - 1:
                self.write(", ")
            self.write(";\n\n")
        for block in self.blocks._.values():
            if block.opcode.startswith("event_") or block.opcode in [
                "control_start_as_clone",
                "procedures_definition",
            ]:
                self.block(block)
                self.write("\n")

    def from_header_find_prototype(
        self, header: dict[str, list[Prototype]], block: Block
    ):
        for prototype in header[block.opcode]:
            if (
                prototype.defaultinput
                and self.menu(block.inputs[prototype.defaultinput[0]])
                != prototype.defaultinput[1]
            ):
                continue
            if (
                prototype.defaultfield
                and block.fields[prototype.defaultfield[0]][0]
                != prototype.defaultfield[1]
            ):
                continue
            return prototype
        return None

    def menu(self, input: list[Any]):
        if input[0] == 1 and isinstance(input[1], str):
            block = self.blocks[input[1]]
            return next(iter(block.fields._.values()))[0]
        return None

    def value(self, value: float | str):
        try:
            value = int(value)
        except ValueError:
            with contextlib.suppress(ValueError):
                value = float(value)

        match value:
            case int() | float():
                self.write(str(value))
            case str():
                value = value.replace("\\", "\\\\").replace('"', '\\"')
                value = '"' + value + '"'
                self.write(value)

    def input(self, block: Block, key: str, default: str | None = None):
        input = block.inputs._.get(key)
        if input is None:
            if default:
                self.write(default)
                return
            raise ValueError(block, key)
        if (value := Input.value(input)) is not None:
            self.value(value)
            return
        if (id := Input.block(input)) is not None:
            self.block(self.blocks[id])
            return
        if name := Input.variable(input):
            self.variable(name)
            return
        if name := Input.list(input):
            self.list(name)
            return
        print(block)

    def block(self, block: Block):
        if block.opcode in self.OPERATORS:
            self.binary_operator(block)
            return
        if self.statement(block):
            return
        if self.reporter(block):
            return
        if func := getattr(self, block.opcode, None):
            func(block)
            return
        print(block)

    def motion_pointindirection(self, block: Block):
        self.input(block, next(iter(block.inputs._.keys())))

    def sensing_touchingobjectmenu(self, block: Block):
        self.value(next(iter(block.fields._.values()))[0])

    sensing_keyoptions = sensing_touchingobjectmenu
    control_create_clone_of_menu = sensing_touchingobjectmenu
    motion_glideto_menu = sensing_touchingobjectmenu
    control_wait = motion_pointindirection

    def statement(self, block: Block):
        prototype = self.from_header_find_prototype(STATEMENTS, block)
        if prototype is None:
            return False
        self.tabwrite(prototype.name + (" " if prototype.inputs else ""))
        for index, key in enumerate(prototype.inputs):
            self.input(block, key)
            if index < len(prototype.inputs) - 1:
                self.write(", ")
        self.write(";\n")
        return True

    def reporter(self, block: Block):
        prototype = self.from_header_find_prototype(REPORTERS, block)
        if prototype is None:
            return False
        self.write(prototype.name + "(")
        for index, key in enumerate(prototype.inputs):
            self.input(block, key)
            if index < len(prototype.inputs) - 1:
                self.write(", ")
        self.write(")")
        return True

    def stack(self, id: str | None):
        if id is None:
            self.write("{}\n")
            return
        self.write("{\n")
        self.level += 1
        while id:
            block = self.blocks[id]
            self.block(block)
            id = block.next
        self.level -= 1
        self.tabwrite("}\n")

    def substack(self, block: Block, key: str):
        try:
            self.stack(block.inputs[key][1])
        except KeyError:
            self.stack(None)

    def event_whenflagclicked(self, block: Block):
        self.write("onflag ")
        self.stack(block.next)

    def control_if(self, block: Block, *, elseif: bool = False):
        self.tabwrite("elif " if elseif else "if ")
        if "CONDITION" in block.inputs._:
            self.input(block, "CONDITION")
        else:
            self.write("false")
        self.write(" ")
        self.substack(block, "SUBSTACK")

    def control_forever(self, block: Block):
        self.tabwrite("forever ")
        self.substack(block, "SUBSTACK")

    def control_repeat_until(self, block: Block):
        self.tabwrite("until ")
        if "CONDITION" in block.inputs._:
            self.input(block, "CONDITION")
        else:
            self.write("false")
        self.write(" ")
        self.substack(block, "SUBSTACK")

    def control_while(self, block: Block):
        self.tabwrite("until not ")
        if "CONDITION" in block.inputs._:
            self.input(block, "CONDITION")
        else:
            self.write("false")
        self.write(" ")
        self.substack(block, "SUBSTACK")

    def control_if_else(self, block: Block, *, elseif: bool = False):
        self.control_if(block, elseif=elseif)
        if substack2 := Input.block(block.inputs._.get("SUBSTACK2")):
            block2 = self.blocks[substack2]
            if block2.opcode == "control_if" and block2.next is None:
                self.control_if(block2, elseif=True)
                return
            if block2.opcode == "control_if_else" and block2.next is None:
                self.control_if_else(block2, elseif=True)
                return
        self.tabwrite("else ")
        self.substack(block, "SUBSTACK2")

    def control_repeat(self, block: Block):
        self.tabwrite("repeat ")
        self.input(block, "TIMES")
        self.write(" ")
        self.substack(block, "SUBSTACK")

    def binary_operator(self, block: Block):
        operator = self.OPERATORS[block.opcode]

        def left():
            parenthesis = False
            if id := Input.block(block.inputs._.get(operator.left)):
                left = self.blocks[id]
                if self.OPERATORS[left.opcode].precedence < operator.precedence:
                    parenthesis = True

            if parenthesis:
                self.write("(")
            self.input(block, operator.left, "false")
            if parenthesis:
                self.write(")")

        def right():
            parenthesis = False
            if id := Input.block(block.inputs._.get(operator.right)):
                right = self.blocks[id]
                if self.OPERATORS[right.opcode].precedence <= operator.precedence:
                    parenthesis = True
            if parenthesis:
                self.write("(")
            self.input(block, operator.right, "false")
            if parenthesis:
                self.write(")")

        if (leftval := Input.value(block.inputs._.get(operator.left))) is not None:
            with contextlib.suppress(ValueError):
                leftval = int(leftval)
                if block.opcode == "operator_subtract":
                    self.write("-")
                    operator = self.OPERATORS["negative"]
                    right()
                    return

        if operator.opcode == "operator_letter_of":
            right()
            self.write("[")
            left()
            self.write("]")
            return

        if operator.opcode == "operator_not":
            if id := Input.block(block.inputs[operator.left]):
                leftb = self.blocks[id]
                if leftb.opcode == "operator_equals":
                    leftb.opcode = "operator_notequals"
                    self.binary_operator(leftb)
                    return
                if leftb.opcode == "operator_lt":
                    leftb.opcode = "operator_ge"
                    self.binary_operator(leftb)
                    return
                if leftb.opcode == "operator_gt":
                    leftb.opcode = "operator_le"
                    self.binary_operator(leftb)
                    return
            self.write(f"{operator.syntax} ")
            left()
            return

        left()
        self.write(f" {operator.syntax} ")
        right()

    def variable(self, name: str):
        self.write(get_name(name))

    def list(self, name: str):
        self.write(get_name(name) + ".join")

    def field(self, block: Block, key: str, *, isname: bool = False):
        field = block.fields[key]
        if isname:
            self.write(get_name(field[0]))
            return
        self.value(field[0])

    def event_whenbroadcastreceived(self, block: Block):
        self.tabwrite("on ")
        self.field(block, "BROADCAST_OPTION")
        self.write(" ")
        self.stack(block.next)

    def event_whenkeypressed(self, block: Block):
        self.tabwrite("onkey ")
        self.field(block, "KEY_OPTION")
        self.write(" ")
        self.stack(block.next)

    def event_whenbackdropswitchesto(self, block: Block):
        self.tabwrite("onbackdrop ")
        self.field(block, "BACKDROP")
        self.write(" ")
        self.stack(block.next)

    def event_whengreaterthan(self, block: Block):
        self.tabwrite(
            "onloudness "
            if block.fields["WHENGREATERTHANMENU"][0] == "LOUDNESS"
            else "ontimer "
        )
        self.input(block, "VALUE")
        self.write(" ")
        self.stack(block.next)

    def event_whenthisspriteclicked(self, block: Block):
        self.tabwrite("onclick ")
        self.stack(block.next)

    def control_start_as_clone(self, block: Block):
        self.tabwrite("onclone ")
        self.stack(block.next)

    def data_setvariableto(self, block: Block):
        self.tabwrite("")
        self.field(block, "VARIABLE", isname=True)
        if id := Input.block(block.inputs["VALUE"]):
            val = self.blocks[id]
            if (
                val.opcode in self.COMPOUND_OPERATORS
                and Input.variable(val.inputs["NUM1"]) == block.fields["VARIABLE"][0]
            ):
                self.write(f" {self.COMPOUND_OPERATORS[val.opcode]}= ")
                self.input(val, "NUM2")
                self.write(";\n")
                return
            if (
                val.opcode == "operator_join"
                and Input.variable(val.inputs["STRING1"]) == block.fields["VARIABLE"][0]
            ):
                self.write(" &= ")
                self.input(val, "STRING2")
                self.write(";\n")
                return
        self.write(" = ")
        self.input(block, "VALUE")
        self.write(";\n")

    def data_changevariableby(self, block: Block):
        self.tabwrite("")
        self.field(block, "VARIABLE", isname=True)
        self.write(" += ")
        self.input(block, "VALUE")
        self.write(";\n")

    def data_showvariable(self, block: Block):
        self.tabwrite("")
        self.field(block, "VARIABLE", isname=True)
        self.write(".show;\n")

    def data_hidevariable(self, block: Block):
        self.tabwrite("")
        self.field(block, "VARIABLE", isname=True)
        self.write(".hide;\n")

    def data_addtolist(self, block: Block):
        self.tabwrite("")
        self.field(block, "LIST", isname=True)
        self.write(".add ")
        self.input(block, "ITEM")
        self.write(";\n")

    def data_deleteoflist(self, block: Block):
        self.tabwrite("")
        self.field(block, "LIST", isname=True)
        self.write(".delete ")
        self.input(block, "INDEX")
        self.write(";\n")

    def data_deletealloflist(self, block: Block):
        self.tabwrite("")
        self.field(block, "LIST", isname=True)
        self.write(" = [];\n")

    def data_insertatlist(self, block: Block):
        self.tabwrite("")
        self.field(block, "LIST", isname=True)
        self.write(" ")
        self.input(block, "INDEX")
        self.write(", ")
        self.input(block, "ITEM")
        self.write(";\n")

    def data_replaceitemoflist(self, block: Block):
        self.tabwrite("")
        self.field(block, "LIST", isname=True)
        self.write("[")
        self.input(block, "INDEX")
        self.write("] = ")
        self.input(block, "ITEM")
        self.write(";\n")

    def data_itemoflist(self, block: Block):
        self.field(block, "LIST", isname=True)
        self.write("[")
        self.input(block, "INDEX")
        self.write("]")

    def data_listcontainsitem(self, block: Block):
        self.field(block, "LIST", isname=True)
        self.write(".contains(")
        self.input(block, "ITEM")
        self.write(")")

    def data_showlist(self, block: Block):
        self.tabwrite("")
        self.field(block, "LIST", isname=True)
        self.write(".show;\n")

    def data_hidelist(self, block: Block):
        self.tabwrite("")
        self.field(block, "LIST", isname=True)
        self.write(".hide;\n")

    def procedures_definition(self, block: Block):
        custom = self.blocks[block.inputs["custom_block"][1]]
        name = custom.mutation.proccode.split("%s")[0]
        if custom.mutation.warp != "true":
            self.tabwrite("nowarp def ")
        else:
            self.tabwrite("def ")
        self.write(get_name(name))
        args = json.loads(custom.mutation.argumentnames)
        self.write(" " + ", ".join(args))
        if args:
            self.write(" ")
        self.stack(block.next)

    def procedures_call(self, block: Block):
        name = block.mutation.proccode.split("%s")[0]
        self.tabwrite(get_name(name) + (" " if block.inputs else ""))
        for index, key in enumerate(block.inputs):
            self.input(block, key)
            if index < len(block.inputs) - 1:
                self.write(", ")
        self.write(";\n")

    def argument_reporter_string_number(self, block: Block):
        self.write("$")
        self.field(block, "VALUE", isname=True)
