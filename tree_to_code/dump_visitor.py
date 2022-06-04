import ast
from ast import *
from typing import Any


class DumpVisitor(ast.NodeVisitor):
    def __init__(self):
        pass

    def visit_BinOp(self, node: BinOp) -> str:
        return f"{self.visit(node.left)} {self.visit(node.op)} {self.visit(node.right)}"

    def visit_Name(self, node: Name) -> Any:
        pass

