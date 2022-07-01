import ast
from typing import Tuple, List
import ctypes


def dump_cpp_text(tree: ast.Module = None, filename: str = None) -> dict:
    text, signatures = dump_module(tree)
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
    dump_dict = {
        ast.AnnAssign: dump_ann_assign,
        ast.Assign: dump_assign,
        ast.AugAssign: dump_aug_assign,
        ast.Name: dump_name,
        ast.Constant: dump_constant,
        ast.BinOp: dump_bin_op,
        ast.UnaryOp: dump_unary_op,
        ast.BoolOp: dump_bool_op,
        ast.Return: dump_return,
        ast.Compare: dump_compare,
        ast.Call: dump_call
    }
    res = dump_dict[type(module)](module)
    return res


def dump_compare(module: ast.Compare) -> str:
    op_dict = {
        ast.Eq: "==",
        ast.NotEq: "!=",
        ast.Lt: "<",
        ast.LtE: "<=",
        ast.Gt: ">=",
        ast.GtE: ">"
    }
    op = module.ops[0]
    op_sign = op_dict[type(op)]
    left = dump_expr(module.left)
    right = dump_expr(module.comparators[0])
    return f"({left} {op_sign} {right})"


def dump_name(module: ast.Name) -> str:
    res = ""
    res = module.id
    return res


def dump_constant(module: ast.Constant) -> str:
    const_dict = {
        True: "true",
        False: "false"
    }
    value = module.value
    if value in const_dict.keys():
        return const_dict[value]
    return str(value)


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
    res = ""
    left = dump_expr(module.left)
    right = dump_expr(module.right)
    op = module.op
    bin_op_signs = {
        ast.Add: "+",
        ast.Sub: "-",
        ast.Div: "/",
        ast.FloorDiv: "/",
        ast.Mult: "*",
        ast.Mod: "%",
        ast.LShift: "<<",
        ast.BitAnd: "&",
        ast.RShift: ">>",
        ast.BitOr: "|",
        ast.BitXor: "^"
    }
    op_sign = bin_op_signs[type(op)]
    return f"({left} {op_sign} {right})"


def dump_unary_op(module: ast.UnaryOp) -> str:
    unary_dict = {
        ast.UAdd: "+",
        ast.USub: "-",
        ast.Not: "!",
        ast.Invert: "~"
    }
    operand = dump_expr(module.operand)
    op = module.op
    op_sign = unary_dict[type(op)]
    return f"({op_sign}{operand})"


def dump_aug_assign(module: ast.AugAssign):
    aug_op_dict = {
        ast.Add: "+=",
        ast.Sub: "-=",
        ast.Div: "/=",
        ast.FloorDiv: "/=",
        ast.Mult: "*=",
        ast.Mod: "%=",
        ast.LShift: "<<=",
        ast.RShift: ">>=",
        ast.BitAnd: "&=",
        ast.BitOr: "|=",
        ast.BitXor: "^="
    }
    target = dump_expr(module.target)
    value = dump_expr(module.value)
    op = module.op
    aug_op_sign = aug_op_dict[type(op)]
    return f"{target} {aug_op_sign} {value}"


def dump_bool_op(module: ast.BoolOp) -> str:
    bool_op_dict = {
        ast.And: "&&",
        ast.Or: "||"
    }
    left = dump_expr(module.values[0])
    right = dump_expr(module.values[1])
    op = module.op
    op_sign = bool_op_dict[type(op)]
    return f"({left} {op_sign} {right})"


def dump_return(module: ast.Return) -> str:
    value = dump_expr(module.value)
    return f"return {value}"


def dump_call(module: ast.Call) -> str:
    func = dump_expr(module.func)
    args = ", ".join([dump_expr(arg) for arg in module.args])
    return f"{func}({args})"


def dump_type(module: ast.Name) -> str:
    type_dict = {
        "int": "int",
        "float": "double",
        "bool": "bool"
    }
    return type_dict[module.id]


def ctype_convert(type_str: str):
    type_dict = {
        "int": ctypes.c_int,
        "double": ctypes.c_double,
        "bool": ctypes.c_bool
    }
    return type_dict[type_str]
