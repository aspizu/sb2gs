from typing import Any, TypedDict

Input = list[Any]
Field = tuple[str, str | None]


class Block(TypedDict):
    opcode: str
    next: str | None
    parent: str | None
    inputs: dict[str, Input]
    fields: dict[str, Field]
    shadow: bool
    topLevel: bool


class Mutation(TypedDict):
    argumentnames: str


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
    blocks: dict[str, Block | MutatedBlock]


class Project(TypedDict):
    targets: list[Sprite]
