import ast

source = """
def sum(x: int, y: int) -> int:
    res: int = x + y
    return res
"""
ast_object = ast.parse(source)

print(ast.dump(ast_object, indent=4))