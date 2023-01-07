import importlib.resources


def gdsl_read(filename: str) -> dict[str, str]:
    statements: dict[str, str] = {}
    for line in importlib.resources.open_text("res", filename):
        line = line.strip()
        if not line or line[0] == "#":
            continue
        name, _, opcode = [i.strip() for i in line.split("|")]
        statements[opcode] = name
    return statements


statements: dict[str, str] = gdsl_read("statements.txt")
reporters: dict[str, str] = gdsl_read("reporters.txt")
