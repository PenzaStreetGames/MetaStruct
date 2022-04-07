import ast


def get_python_text(module: str) -> str:
    with open(module, "r", encoding="utf-8") as infile:
        text = infile.read()
    return text


def get_python_tree(text: str = None, filename: str = None):
    if text is None:
        if filename is not None:
            text = get_python_text(filename)
        else:
            raise Exception("Nothing to parse")
    parsed = ast.parse(text)
    print(ast.dump(parsed, indent=4))
    return parsed
