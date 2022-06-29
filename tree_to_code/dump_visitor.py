import ast
from ast import *
from typing import Any, Tuple, Iterable
import ctypes


def dump_cpp_text(tree: ast.Module = None, filename: str = None) -> dict:
    text, signatures = DumpVisitor().visit(tree)
    with open(filename, "w", encoding="utf-8") as outfile:
        outfile.write(text)
    return signatures


def dump_type(str_type: str) -> str:
    match str_type:
        case "int":
            return "int"
        case "float":
            return "double"
        case "bool":
            return "bool"
        case _:
            raise Exception(f"unsupported type {str_type}")


def ctype_convert(type_str: str):
    match type_str:
        case "int":
            return ctypes.c_int
        case "double":
            return ctypes.c_double
        case "bool":
            return ctypes.c_bool
        case _:
            raise Exception(f"unsupported type str {type_str}")


class DumpVisitor(ast.NodeVisitor):
    def __init__(self):
        pass

    def visit_Module(self, node: Module) -> Tuple[str, dict]:
        res, signatures = "", {}
        for elem in node.body:
            match elem:
                case FunctionDef(name=name):
                    func_text, signature = self.visit(elem)
                    res += func_text + "\n"
                    signatures[name] = signature
        return res, signatures

    def visit_FunctionDef(self, node: FunctionDef) -> Tuple[str, dict]:
        ret_type = self.visit(node.returns)
        name = node.name
        args, args_signature = [], []
        for arg in node.args.args:
            arg, arg_type = self.visit(arg)
            args.append(f"{arg_type} {arg}")
            args_signature.append(ctype_convert(arg_type))
        args = ", ".join(args)
        res = f"extern \"C\" {ret_type} {name}({args}) {{\n"
        res += self.dump_body(node.body) + "}"
        signature = {
            "argtypes": args_signature,
            "restype": ctype_convert(ret_type)
        }
        return res, signature

    def visit_arg(self, node: arg) -> Tuple[str, str]:
        return node.arg, self.visit(node.annotation)

    def dump_body(self, nodes: Iterable[stmt]) -> str:
        res = ""
        for node in nodes:
            match node:
                case While() | If():
                    res += self.visit(node)
                case _:
                    res += self.visit(node) + ";\n"
        space = " " * 4
        res = space + res.replace("\n", "\n" + space).rstrip(space)
        return res

    def visit_While(self, node: While) -> str:
        condition = self.visit(node.test)
        res = f"while {condition} {{\n"
        res += self.dump_body(node.body) + "}\n"
        return res

    def visit_If(self, node: If) -> str:
        condition = self.visit(node.test)
        res = f"if ({condition}) {{\n"
        res += self.dump_body(node.body) + "}\n"
        match orelse := node.orelse:
            case If():
                res += self.visit(orelse)
            case []:
                pass
            case _:
                else_body = self.dump_body(orelse)
                res += f"{{\n{else_body}}}\n"
        return res

    def visit_AnnAssign(self, node: AnnAssign) -> str:
        return f"{self.visit(node.annotation)} {self.visit(node.target)} = {self.visit(node.value)}"

    def visit_Assign(self, node: Assign) -> str:
        return f"{self.visit(node.targets[0])} = {self.visit(node.value)}"

    def visit_Constant(self, node: Constant) -> str:
        match node:
            case Constant(value=True):
                return "true"
            case Constant(value=False):
                return "false"
            case _:
                return str(node.value)

    def visit_UnaryOp(self, node: UnaryOp) -> str:
        return f"{self.visit(node.op)}{self.visit(node.operand)}"

    def visit_BinOp(self, node: BinOp) -> str:
        return f"({self.visit(node.left)} {self.visit(node.op)} {self.visit(node.right)})"

    def visit_Name(self, node: Name) -> str:
        match node.id:
            case "int" | "bool" | "float":
                return dump_type(node.id)
            case _:
                return node.id

    def visit_BoolOp(self, node: BoolOp) -> str:
        return f"({self.visit(node.values[0])} {self.visit(node.op)} {self.visit(node.values[1])})"

    def visit_Return(self, node: Return) -> str:
        return f"return {self.visit(node.value)}"

    def visit_AugAssign(self, node: AugAssign) -> str:
        return f"{self.visit(node.target)} {self.visit(node.op)}= {self.visit(node.value)}"

    def visit_Compare(self, node: Compare) -> str:
        return f"({self.visit(node.left)} {self.visit(node.ops[0])} {self.visit(node.comparators[0])})"

    def visit_Call(self, node: Call) -> str:
        args = ", ".join(map(self.visit, node.args))
        return f"{self.visit(node.func)}({args})"

    def visit_Break(self, node: Break) -> str:
        return "break"

    def visit_Continue(self, node: Continue) -> str:
        return "continue"

    def visit_Add(self, node: Add) -> str:
        return "+"

    def visit_Sub(self, node: Sub) -> str:
        return "-"

    def visit_Div(self, node: Div) -> str:
        return "/"

    def visit_FloorDiv(self, node: FloorDiv) -> str:
        return "/"

    def visit_Mult(self, node: Mult) -> str:
        return "*"

    def visit_Mod(self, node: Mod) -> str:
        return "%"

    def visit_LShift(self, node: LShift) -> str:
        return "<<"

    def visit_RShift(self, node: RShift) -> str:
        return ">>"

    def visit_BitAnd(self, node: BitAnd) -> str:
        return "&"

    def visit_BitOr(self, node: BitOr) -> str:
        return "|"

    def visit_BitXor(self, node: BitXor) -> str:
        return "^"

    def visit_Eq(self, node: Eq) -> str:
        return "=="

    def visit_NotEq(self, node: NotEq) -> str:
        return "!="

    def visit_Lt(self, node: Lt) -> str:
        return "<"

    def visit_LtE(self, node: LtE) -> str:
        return "<="

    def visit_Gt(self, node: Gt) -> str:
        return ">"

    def visit_GtE(self, node: GtE) -> str:
        return ">="

    def visit_UAdd(self, node: UAdd) -> str:
        return "+"

    def visit_USub(self, node: USub) -> str:
        return "-"

    def visit_Not(self, node: Not) -> str:
        return "!"

    def visit_Invert(self, node: Invert) -> str:
        return "~"

    def visit_And(self, node: And) -> str:
        return "&&"

    def visit_Or(self, node: Or) -> str:
        return "||"
