# sb2gs

Decompile Scratch projects into
[**goboscript**](https://github.com/aspizu/goboscript) projects automatically.

### Installation

Use [uv](https://docs.astral.sh/uv) to install sb2gs globally.

```bash
uv tool install git+https://github.com/aspizu/sb2gs
```

You can also use [nix flakes](https://wiki.nixos.org/wiki/Flakes) to install and
develop sb2gs. The provided flake exports `packages.${system}.default` for
installation, and provides a devShell (accessible in repo using `nix develop`)
which builds an `editable` version of sb2gs.

### Usage

You can directly download and decompile a Scratch project from its ID.

```bash
sb2gs --id 12345678 my_project_name --verify
```

`--verify` requires goboscript to be installed.

```
usage: sb2gs [-h] [--overwrite] [--id ID] [--verify] input [output]

positional arguments:
  input
  output

options:
  -h, --help   show this help message and exit
  --overwrite
  --id ID      Download the project with this ID.
  --verify     Invoke goboscript to verify that the decompiled code is valid. This does not indicate that the decompiled code is equivalent
               to the original.
```
