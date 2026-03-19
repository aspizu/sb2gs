import json
from typing import TYPE_CHECKING
from zipfile import ZipFile

import httpx

if TYPE_CHECKING:
    from pathlib import Path


def download_sb3(id: str, outfile: str | Path) -> None:
    res = httpx.get(f"https://api.scratch.mit.edu/projects/{id}")
    res.raise_for_status()
    token = res.json()["project_token"]
    res = httpx.get(f"https://projects.scratch.mit.edu/{id}?token={token}")
    res.raise_for_status()
    data = res.json()
    assets = {
        *(
            costume["md5ext"]
            for target in data["targets"]
            for costume in target["costumes"]
        ),
        *(
            costume["md5ext"]
            for target in data["targets"]
            for costume in target["sounds"]
        ),
    }
    with ZipFile(outfile, "w") as zf:
        zf.writestr("project.json", json.dumps(data))
        for md5ext in assets:
            res = httpx.get(
                f"https://assets.scratch.mit.edu/internalapi/asset/{md5ext}/get/"
            )
            res.raise_for_status()
            content = res.read()
            zf.writestr(md5ext, content)
