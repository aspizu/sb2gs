from typing import Any, TypedDict, Optional,Union

Input = list[Any]
Field = tuple[str, Optional[str]]


class Block(TypedDict):
    opcode: str
    next: Optional[str]
    parent: Optional[str]
    inputs: dict[str, Input]
    fields: dict[str, Field]
    shadow: bool
    topLevel: bool


class Mutation(TypedDict):
    proccode: str
    argumentnames: str
    warp: str


class MutatedBlock(Block):
    mutation: Mutation


class Costume(TypedDict):
    name: str
    md5ext: str


class Sprite(TypedDict):
    name: str
    variables: dict[str, tuple[str, Any]]
    lists: dict[str, tuple[str, Any]]
    costumes: list[Costume]
    blocks: dict[str, Union[Block, MutatedBlock]]


class Project(TypedDict):
    targets: list[Sprite]
