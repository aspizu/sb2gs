from __future__ import annotations

import contextlib
import json
import re
import string
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TextIO, final

from . import nblk
from .print import print
from .sb3 import Input, Target

if TYPE_CHECKING:
    from .sb3 import Block

pcode = re.compile(r"%[bs]")


def get_name(name: str):
    if name.strip() in ("//", "#"):
        return "REM"
    name = "_".join(name.split())
    name = name.replace("!", "_BNG_")
    name = name.replace(".", "_DOT_")
    name = name.replace("$", "_PHP_")
    if name[0] in string.digits:
        name = "z" + name
    return "".join(i for i in name if i in string.ascii_letters + string.digits + "_")


@dataclass
class BinaryOperator:
    opcode: str
    syntax: str
    precedence: int
    left: str
    right: str


@final
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
    "operator_equals"    :( "=="  , 0          , "OPERAND1" , "OPERAND2" ),
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
    #------------------:-----#    "operator_add"     : "+" ,
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
        # Generate var declarations with default values from the project
        for variable_id, variable_data in self.target.variables._.items():
            variable_name = variable_data[0]  # Variable name
            default_value = variable_data[1]  # Default value from project
            self.tabwrite("var ")
            self.write(get_name(variable_name))
            self.write(" = ")
            self.value(default_value)
            self.write(";\n")

        if len(self.target.variables) > 0:
            self.write("\n")

        for i, lst in enumerate(self.target.lists._.items()):
            self.tabwrite("list ")
            self.write(get_name(lst[1][0]))
            self.write(";\n")

        for block in self.blocks._.values():
            if isinstance(block, list):
                continue
            if block.opcode == "procedures_definition" and block.topLevel:
                self.statement(block)

        for i, lst in enumerate(self.target.lists._.items()):
            self.tabwrite("list ")
            self.write(get_name(lst[1][0]))
            self.write(";\n")

        self.tabwrite("costumes ")
        for i, costume in enumerate(self.target.costumes):
            self.value(f"{self.target.name}/{costume.name}.{costume.dataFormat}")
            if i < len(self.target.costumes) - 1:
                self.write(", ")
        self.write(";\n\n")
        for block in self.blocks._.values():
            if isinstance(block, list):
                continue
            if (
                block.opcode.startswith("event_")
                and block.opcode not in ["event_broadcast", "event_broadcastandwait"]
                or block.opcode in ["control_start_as_clone", "procedures_definition"]
            ):
                self.block(block)
                self.write("\n")

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
                if value in ("Infinity", "-Infinity"):
                    raise ValueError from None
                value = float(value)

        match value:
            case int() | float():
                self.write(str(value))
            case str():
                self.str(value)

    def str(self, value: str):
        value = value.replace("\\", "\\\\").replace('"', '\\"')
        value = '"' + value + '"'
        self.write(value)

    def input(self, block: Block, key: str, default: str | None = None):
        if key == "CONDITION" or key == "CONDITION2":
            default = "false"
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
        print(f'input "{key}":', block)

    def block(self, block: Block):
        if func := getattr(self, block.opcode, None):
            func(block)
            return
        if block.opcode in self.OPERATORS:
            self.binary_operator(block)
            return
        if self.statement(block):
            return
        if self.reporter(block):
            return
        print("block:", block)

    def sensing_touchingobjectmenu(self, block: Block):
        self.value(next(iter(block.fields._.values()))[0])

    sensing_keyoptions = sensing_touchingobjectmenu
    control_create_clone_of_menu = sensing_touchingobjectmenu
    motion_glideto_menu = sensing_touchingobjectmenu
    # control_wait = motion_pointindirection
    looks_costume = sensing_touchingobjectmenu
    looks_backdrops = sensing_touchingobjectmenu
    sensing_distancetomenu = sensing_touchingobjectmenu
    sound_sounds_menu = sensing_touchingobjectmenu
    motion_goto_menu = sensing_touchingobjectmenu
    motion_pointtowards_menu = sensing_touchingobjectmenu

    def statement(self, block: Block):
        prototype = nblk.nblk(self, block)
        if not prototype:
            return False
        self.tabwrite(prototype.name + (" " if prototype.args else ""))
        for index, key in enumerate(prototype.args):
            self.input(block, key)
            if index < len(prototype.args) - 1:
                self.write(", ")
        self.write(";\n")
        return True

    def reporter(self, block: Block):
        prototype = nblk.nblkreporter(self, block)
        if not prototype:
            return False
        self.write(prototype.name + "(")
        for index, key in enumerate(prototype.args):
            self.input(block, key)
            if index < len(prototype.args) - 1:
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
                if (
                    left.opcode in self.OPERATORS
                    and self.OPERATORS[left.opcode].precedence < operator.precedence
                ):
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
                if (
                    right.opcode in self.OPERATORS
                    and self.OPERATORS[right.opcode].precedence <= operator.precedence
                ):
                    parenthesis = True
            if parenthesis:
                self.write("(")
            self.input(block, operator.right, "false")
            if parenthesis:
                self.write(")")

        if (leftval := Input.value(block.inputs._.get(operator.left))) is not None:
            with contextlib.suppress(ValueError):
                leftval = float(leftval)

            if block.opcode == "operator_subtract" and (leftval == 0 or leftval == ""):
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
            if id := Input.block(block.inputs._.get(operator.left)):
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

    def field(
        self, block: Block, key: str, *, isname: bool = False, isstr: bool = False
    ):
        field = block.fields[key]
        if isname:
            self.write(get_name(field[0]))
            return
        if isstr:
            self.str(field[0])
            return
        self.value(field[0])

    def event_whenbroadcastreceived(self, block: Block):
        self.tabwrite("on ")
        self.field(block, "BROADCAST_OPTION")
        self.write(" ")
        self.stack(block.next)

    def event_whenkeypressed(self, block: Block):
        self.tabwrite("onkey ")
        self.field(block, "KEY_OPTION", isstr=True)
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
        self.tabwrite("show ")
        self.field(block, "VARIABLE", isname=True)
        self.write(";\n")

    def data_hidevariable(self, block: Block):
        self.tabwrite("hide ")
        self.field(block, "VARIABLE", isname=True)
        self.write(";\n")

    def data_addtolist(self, block: Block):
        self.tabwrite("add ")
        self.input(block, "ITEM")
        self.write(" to ")
        self.field(block, "LIST", isname=True)
        self.write(";\n")

    def data_deleteoflist(self, block: Block):
        self.tabwrite("delete ")
        self.field(block, "LIST", isname=True)
        self.write("[")
        self.input(block, "INDEX")
        self.write("];\n")

    def data_lengthoflist(self, block: Block):
        self.write("length(")
        self.field(block, "LIST", isname=True)
        self.write(")")

    def data_deletealloflist(self, block: Block):
        self.tabwrite("delete ")
        self.field(block, "LIST", isname=True)
        self.write(";\n")

    def data_insertatlist(self, block: Block):
        self.tabwrite("insert ")
        self.input(block, "ITEM")
        self.write(" at ")
        self.field(block, "LIST", isname=True)
        self.write("[")
        self.input(block, "INDEX")
        self.write("];\n")

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
        # TODO: remove parenthesis
        self.write("(")
        self.write("(")
        self.input(block, "ITEM")
        self.write(")")
        self.write(" in ")
        self.field(block, "LIST", isname=True)
        self.write(")")

    def data_itemnumoflist(self, block: Block):
        self.write("(")
        self.write("(")
        self.input(block, "ITEM")
        self.write(")")
        self.write(" in ")
        self.field(block, "LIST", isname=True)
        self.write(")")

    def data_showlist(self, block: Block):
        self.tabwrite("show ")
        self.field(block, "LIST", isname=True)
        self.write(";\n")

    def data_hidelist(self, block: Block):
        self.tabwrite("hide ")
        self.field(block, "LIST", isname=True)
        self.write(";\n")

    def procedures_definition(self, block: Block):
        custom = self.blocks[block.inputs["custom_block"][1]]
        name = pcode.split(custom.mutation.proccode)[0]
        if custom.mutation.warp != "true":
            self.tabwrite("nowarp proc ")
        else:
            self.tabwrite("proc ")
        self.write(get_name(name))
        args = [get_name(i) for i in json.loads(custom.mutation.argumentnames)]
        self.write(" " + ", ".join(args))
        if args:
            self.write(" ")
        self.stack(block.next)

    def procedures_call(self, block: Block):
        name = pcode.split(block.mutation.proccode)[0]
        args = json.loads(block.mutation.argumentids)
        self.tabwrite(get_name(name) + (" " if block.inputs else ""))
        for index, arg_id in enumerate(args):
            if arg_id not in block.inputs:
                self.write("false")
            else:
                self.input(block, arg_id)
            if index < len(args) - 1:
                self.write(", ")
        self.write(";\n")

    def argument_reporter_string_number(self, block: Block):
        self.write("$")
        self.field(block, "VALUE", isname=True)

    def argument_reporter_boolean(self, block: Block):
        # TODO: Implement this properly
        # if block.fields["VALUE"][0] == "is compiled?":
        #    self.write("true")
        #    return
        # self.write("false")
        self.write("$")
        self.field(block, "VALUE", isname=True)

    def sensing_of(self, block: Block):
        self.write('"THING OF THING BLOCK NOT IMPLEMENTED"')
