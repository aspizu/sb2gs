# sb2gs

Use sb2gs to turn your Scratch projects into [goboscript](https://github.com/aspizu/goboscript) projects.

sb2gs decompiles Scratch code into idiomatic goboscript code.

It will make use of goboscript features such as compound assignments (`variable *= multiplier`), if else if chains, etc.

sb2gs automatically renames variables.

## Installation

```sh
git clone https://github.com/aspizu/sb2gs
cd sb2gs
pip install --break-system-packages --editable .
#           ^^^^^^^^^^^^^^^^^^^^^^^ Might not be needed on older systems.
```


### To update, run this command inside the repository root.
```sh
git pull
```

## Usage

```sh
python -m sb2gs --input project.sb3 --output project_dir/
```
