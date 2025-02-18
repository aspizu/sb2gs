from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Literal, TypeVar

T = TypeVar("T")


@dataclass
class Namespace(Generic[T]):
    _: dict[str, T]

    def __getattr__(self, key: str):
        try:
            return self._[key]
        except KeyError:
            raise AttributeError(key) from None

    def __getitem__(self, key: str):
        return self._[key]

    def __repr__(self):
        return repr(self._)

    def __str__(self):
        return str(self._)

    def __len__(self):
        return len(self._)

    def __iter__(self):
        return iter(self._)

    def __rich__(self) -> Any:
        def rich(v: Any) -> Any:
            match v:
                case Namespace():
                    return v.__rich__()
                case list():
                    return [rich(i) for i in v]
                case _:
                    return v

        return {k: rich(v) for k, v in self._.items()}


class Block(Namespace[Any]):
    opcode: str
    next: str | None
    parent: str | None
    inputs: Namespace[list[Any]]
    fields: Namespace[tuple[str, str | None]]
    shadow: bool
    topLevel: bool
    x: float
    y: float
    mutation: Mutation


class Mutation(Namespace[Any]):
    tagName: Literal["mutation"]
    children: list[None]
    proccode: str
    argumentids: str
    argumentnames: str
    argumentdefaults: str
    warp: str


class Comment(Namespace[Any]):
    ...


class Costume(Namespace[Any]):
    name: str
    bitmapResolution: float
    dataFormat: str
    assetId: str
    md5ext: str
    rotationCenterX: float
    rotationCenterY: float


class Sound(Namespace[Any]):
    ...


class Target(Namespace[Any]):
    isStage: bool
    name: str
    variables: Namespace[tuple[str, float | str]]
    lists: Namespace[tuple[str, list[float | str]]]
    broadcasts: Namespace[str]
    blocks: Namespace[Block]
    comments: Namespace[Comment]
    currentCostume: int
    costumes: list[Costume]
    sounds: list[Sound]
    volume: float
    layerOrder: int
    tempo: float
    videoTransparency: float
    videoState: str
    textToSpeechLanguage: str | None


class Monitor(Namespace[Any]):
    id: str
    mode: str
    opcode: str
    params: Namespace[str]
    spriteName: str | None
    value: float | list[Any]
    width: float
    height: float
    x: float
    y: float
    visible: bool
    sliderMin: float
    sliderMax: float
    isDiscrete: bool


class Meta(Namespace[Any]):
    semver: str
    vm: str
    agent: str


class Project(Namespace[Any]):
    targets: list[Target]
    monitors: list[Monitor]
    extensions: list[str]
    meta: Meta


class Input:
    @staticmethod
    def block(input: list[Any] | None) -> str | None:
        if input is None:
            return None
        if input[0] in (1, 2, 3) and isinstance(input[1], str):
            return input[1]
        return None

    @staticmethod
    def value(input: list[Any] | None) -> str | None:
        if input is None:
            return None
        if (
            input[0] in (1,) and isinstance(input[1], list)
            # and input[1][0] in (4, 5, 6, 7, 8, 9, 10)
        ):
            return input[1][1]
        return None

    @staticmethod
    def variable(input: list[Any] | None) -> str | None:
        if input is None:
            return None
        if isinstance(input[1], list) and input[1][0] == 12:
            return input[1][1]
        return None

    @staticmethod
    def list(input: list[Any] | None) -> str | None:
        if input is None:
            return None
        if isinstance(input[1], list) and input[1][0] == 13:
            return input[1][1]
        return None
