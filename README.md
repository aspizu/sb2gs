## Installation

Install Python >= 3.13.0, then run:

```shell
git clone https://github.com/aspizu/sb2gs
cd sb2gs
python -m pip install --editable .
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
