from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

if TYPE_CHECKING:
    from collections.abc import Generator


class JSONDict[T = Any](dict[str, T]):
    def to_dict(self) -> dict[str, Any]:
        return {
            k: v._.to_dict() if isinstance(v, JSONObject) else v
            for k, v in self.items()
        }


class JSONObject[T = Any]:
    def __init__(self, dictionary: dict[str, T]) -> None:
        self._: JSONDict[T] = JSONDict[T](dictionary)

    @override
    def __repr__(self) -> str:
        return repr(self._)

    def __rich_repr__(self) -> Generator[dict[str, T]]:
        yield self._

    def __contains__(self, key: str) -> bool:
        return key in self._

    def __getattr__(self, name: str, /) -> T:
        try:
            return self._[name]
        except KeyError:
            msg = f"{self.__class__.__name__!r} has no attribute {name!r}"
            raise AttributeError(msg) from None
