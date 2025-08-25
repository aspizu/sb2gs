## Installation

If you installed goboscript using the auto-install script, then sb2gs should be already installed.

Install uv and run.

```shell
uv tool install git+https://github.com/aspizu/sb2gs
```

## Usage

```
usage: sb2gs [-h] [--overwrite] [--verify] input [output]
positional arguments:
  input
  output

options:
  -h, --help   show this help message and exit
  --overwrite
  --verify     Invoke goboscript to verify that the decompiled code is valid. This does not indicate that the decompiled code
               is equivalent to the original.
```
