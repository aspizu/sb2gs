import json
import shutil
from pathlib import Path
from zipfile import ZipFile

from codegen import CodeGen
from sb3 import Project, Sprite


class Builder:
    def __init__(self, input: Path, output: Path) -> None:
        self.input = input
        self.output = output
        try:
            shutil.rmtree(output)
        except FileNotFoundError:
            pass
        output.mkdir()

        with ZipFile(self.input, "r") as sb3:
            self.extract_costumes(sb3)
            self.build_project(json.load(sb3.open("project.json")))

    def extract_costumes(self, sb3: ZipFile) -> None:
        for costume in sb3.filelist:
            if costume.filename != "project.json":
                sb3.extract(costume, self.output)

    def build_project(self, project: Project) -> None:
        for sprite in project["targets"]:
            self.build_sprite(sprite)

    def build_sprite(self, sprite: Sprite) -> None:
        if sprite["name"] == "Stage":
            sprite["name"] = "stage"
            self.globals: list[str] = [i[0] for i in sprite["variables"].values()]
            self.listglobals: list[str] = [i[0] for i in sprite["lists"].values()]
        with open(self.output / (sprite["name"] + ".gs"), "w") as out:
            for costume in sprite["costumes"]:
                name = costume["name"] + Path(costume["md5ext"]).suffix
                file = self.output / costume["md5ext"]
                if file.is_file():
                    file.rename(self.output / str(name).replace("/", "_"))
            CodeGen(out, sprite, self.globals, self.listglobals)
