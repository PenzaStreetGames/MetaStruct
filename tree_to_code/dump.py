import ast
import ctypes
from typing import List, Optional, Tuple
from tree_to_code.dump_visitor import DumpVisitor


def dump_cpp_text(tree: ast.Module = None, filename: str = None) -> dict:
    text, signatures = DumpVisitor().visit(tree)
    with open(filename, "w", encoding="utf-8") as outfile:
        outfile.write(text)
    return signatures


def dump_module(module: ast.Module) -> Tuple[str, dict]:
    res = ""
    signatures = {}
    for elem in module.body:
        if isinstance(elem, ast.FunctionDef):
            func_text, signature = dump_function(elem)
            res += func_text + "\n"
            signatures[elem.name] = signature
    return res, signatures


def dump_function(module: ast.FunctionDef) -> Tuple[str, dict]:
    res = ""
    ret_type = dump_type(module.returns)
    name = module.name
    args, args_signature = dump_function_args(module.args)
    res += f"extern \"C\" {ret_type} {name}({args}) " + "{\n"
    dumped_body = dump_body(module.body, indent=True)
    res += dumped_body
    res += "}"
    signature = {
        "argtypes": args_signature,
        "restype": ctype_convert(ret_type)
    }
    return res, signature


def dump_function_args(args: ast.arguments) -> Tuple[str, list]:
    args_list = []
    args_signature = []
    for arg in args.args:
        arg_name = arg.arg
        arg_type = dump_type(arg.annotation)
        args_list.append(f"{arg_type} {arg_name}")
        args_signature.append(ctype_convert(arg_type))
    return ', '.join(args_list), args_signature


def dump_body(module: List[ast.stmt], indent=True) -> str:
    res = ""
    body_dumpers = {
        ast.While: dump_while,
        ast.If: dump_if
    }
    for elem in module:
        expr_class = type(elem)
        if expr_class in body_dumpers.keys():
            res += body_dumpers[expr_class](elem)
        else:
            res += dump_expr(elem) + ";\n"
    if indent:
        res = "    " + res.replace("\n", "\n    ").rstrip("    ")
    return res


def dump_while(module: ast.While) -> str:
    res = ""
    condition = dump_expr(module.test)
    res += f"while ({condition}) {{\n"
    body = dump_body(module.body, indent=True)
    res += body
    res += "}\n"
    return res


def dump_if(module: ast.If) -> str:
    res = ""
    condition = dump_expr(module.test)
    res += f"if {condition} {{\n"
    body = dump_body(module.body, indent=True)
    res += body + "}\n"
    orelse = module.orelse
    if orelse:
        res += "else "
        first = orelse[0]
        if isinstance(first, ast.If):
            res += dump_if(first)
        else:
            else_body = dump_body(orelse)
            res += f"{{\n{else_body}}}\n"

    return res


def dump_expr(module: ast.expr) -> str:
    match module_type := type(module):
        case ast.AnnAssign:
            dumper = dump_ann_assign
        case ast.Assign:
            dumper = dump_assign
        case ast.Name:
            dumper = dump_name
        case ast.Constant:
            dumper = dump_constant
        case ast.BinOp:
            dumper = dump_bin_op
        case ast.UnaryOp:
            dumper = dump_unary_op
        case ast.BoolOp:
            dumper = dump_bool_op
        case ast.Return:
            dumper = dump_return
        case ast.AugAssign:
            dumper = dump_aug_assign
        case ast.Compare:
            dumper = dump_compare
        case ast.Call:
            dumper = dump_call
        case _:
            raise Exception(f"unsupported expr type {module_type}")
    res = dumper(module)
    return res


def dump_compare(module: ast.Compare) -> str:
    op = module.ops[0]
    match op_type := type(op):
        case ast.Eq:
            op_sign = "=="
        case ast.NotEq:
            op_sign = "!="
        case ast.Lt:
            op_sign = "<"
        case ast.LtE:
            op_sign = "<="
        case ast.Gt:
            op_sign = ">"
        case ast.GtE:
            op_sign = ">="
        case _:
            raise Exception(f"unsupported compare type {op_type}")
    left = dump_expr(module.left)
    right = dump_expr(module.comparators[0])
    return f"({left} {op_sign} {right})"


def dump_name(module: ast.Name) -> str:
    res = ""
    res = module.id
    return res


def dump_constant(module: ast.Constant) -> str:
    match module.value:
        case True:
            return "true"
        case False:
            return "false"
        case _:
            return f"{module.value}"


def dump_ann_assign(module: ast.AnnAssign) -> str:
    target = dump_expr(module.target)
    value = dump_expr(module.value)
    target_type = dump_type(module.annotation)
    return f"{target_type} {target} = {value}"


def dump_assign(module: ast.Assign) -> str:
    target = dump_expr(module.targets[0])
    value = dump_expr(module.value)
    return f"{target} = {value}"


def dump_bin_op(module: ast.BinOp) -> str:
    op = module.op
    match module:
        case ast.BinOp(op=ast.Add()):
            op_sign = "+"
        case ast.BinOp(op=ast.Sub()):
            op_sign = "-"
        case ast.BinOp(op=ast.Div()):
            op_sign = "/"
        case ast.BinOp(op=ast.FloorDiv()):
            op_sign = "/"
        case ast.BinOp(op=ast.Mult()):
            op_sign = "*"
        case ast.BinOp(op=ast.Mod()):
            op_sign = "%"
        case ast.BinOp(op=ast.LShift()):
            op_sign = "<<"
        case ast.BinOp(op=ast.RShift()):
            op_sign = ">>"
        case ast.BinOp(op=ast.BitAnd()):
            op_sign = "&"
        case ast.BinOp(op=ast.BitOr()):
            op_sign = "|"
        case ast.BinOp(op=ast.BitXor()):
            op_sign = "^"
        case _:
            raise Exception(f"unsupported bin op type {op_type}")
    left = dump_expr(module.left)
    right = dump_expr(module.right)
    return f"({left} {op_sign} {right})"


def dump_unary_op(module: ast.UnaryOp) -> str:
    operand = dump_expr(module.operand)
    op = module.op
    match op_type := type(op):
        case ast.UAdd:
            op_sign = "+"
        case ast.USub:
            op_sign = "-"
        case ast.Not:
            op_sign = "!"
        case ast.Invert:
            op_sign = "~"
        case _:
            raise Exception(f"unsupported unary op type {op_type}")
    return f"({op_sign}{operand})"


def dump_aug_assign(module: ast.AugAssign):
    target = dump_expr(module.target)
    value = dump_expr(module.value)
    op = module.op
    match op_type := type(op):
        case ast.Add:
            aug_op_sign = "+="
        case ast.Sub:
            aug_op_sign = "-="
        case ast.Div:
            aug_op_sign = "/="
        case ast.FloorDiv:
            aug_op_sign = "/="
        case ast.Mult:
            aug_op_sign = "*="
        case ast.Mod:
            aug_op_sign = "%="
        case ast.LShift:
            aug_op_sign = "<<="
        case ast.RShift:
            aug_op_sign = ">>="
        case ast.BitAnd:
            aug_op_sign = "&="
        case ast.BitOr:
            aug_op_sign = "|="
        case ast.BitXor:
            aug_op_sign = "^="
        case _:
            raise Exception(f"unsupported aug assign type {op_type}")
    return f"{target} {aug_op_sign} {value}"


def dump_bool_op(module: ast.BoolOp) -> str:
    left = dump_expr(module.values[0])
    right = dump_expr(module.values[1])
    op = module.op
    match op_type := type(op):
        case ast.And:
            op_sign = "&&"
        case ast.Or:
            op_sign = "||"
        case _:
            raise Exception(f"unsupported bool op type {op_type}")
    return f"({left} {op_sign} {right})"


def dump_return(module: ast.Return) -> str:
    value = dump_expr(module.value)
    return f"return {value}"


def dump_call(module: ast.Call) -> str:
    func = dump_expr(module.func)
    args = ", ".join([dump_expr(arg) for arg in module.args])
    return f"{func}({args})"


def dump_type(module: ast.Name) -> str:
    res = ""
    match module_type := module.id:
        case "int":
            return "int"
        case "float":
            return "double"
        case "bool":
            return "bool"
        case _:
            raise Exception(f"unsupported type {module_type}")


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
