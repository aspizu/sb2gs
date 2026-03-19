import textwrap
from abc import ABC, abstractmethod
from dataclasses import dataclass

from rich import print


class Widget(ABC):
    @abstractmethod
    def get_width(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_height(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def render(self) -> str:
        raise NotImplementedError


@dataclass
class Text(Widget):
    value: str

    def get_width(self) -> int:
        return len(self.value)

    def get_height(self) -> int:
        return 1

    def render(self) -> str:
        return self.value


@dataclass
class Block(Widget):
    opening: str
    closing: str
    children: list[Widget]
    comma: bool = True
    expand: bool = False

    def get_width(self) -> int:
        if self.expand:
            return max(
                len(self.opening),
                len(self.closing),
                *(4 + child.get_width() for child in self.children),
            )
        return sum(
            (
                len(self.opening),
                *(child.get_width() for child in self.children),
                len(self.closing),
                max(len(self.children) - 1, 0) * 2 if self.comma else 0,
            )
        )

    def get_height(self) -> int:
        if self.expand:
            return 2 + sum(child.get_height() for child in self.children)
        return 1

    def render(self) -> str:
        if self.expand:
            out = self.opening + "\n"
            for child in self.children:
                out += textwrap.indent(child.render(), " " * 4)
                out += ",\n"
            out += self.closing
            return out

        out = self.opening
        for i, child in enumerate(self.children):
            if self.comma and i != 0:
                out += ", "
            out += child.render()
        out += self.closing
        return out


MAX_WIDTH = 88


def expand(tree: Widget, max_width: int = MAX_WIDTH) -> None:
    if not isinstance(tree, Block):
        return
    if tree.get_width() <= max_width:
        return
    tree.expand = True
    for child in tree.children:
        expand(child, max_width - 4)


if __name__ == "__main__":
    tree = Block(
        "{",
        "}",
        [
            Text("one"),
            Text("two"),
            Text("three"),
            Text("four"),
            Text("five"),
            Block(
                "{",
                "}",
                [
                    Text("one"),
                    Text("two"),
                    Text("three"),
                    Text("four"),
                    Text("five"),
                    Block(
                        "{",
                        "}",
                        [
                            Text("one"),
                            Text("two"),
                            Text("three"),
                            Text("four"),
                            Text("five"),
                        ],
                    ),
                ],
            ),
        ],
    )
    expand(tree)
    print(tree.render())
