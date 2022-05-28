import ast
from typing import List, Optional


def dump_cpp_text(tree: ast.Module = None, filename: str = None) -> str:
    text = dump_module(tree)
    with open(filename, "w", encoding="utf-8") as outfile:
        outfile.write(text)
    return text


def dump_module(module: ast.Module) -> str:
    res = ""
    for elem in module.body:
        if isinstance(elem, ast.FunctionDef):
            res += dump_function(elem) + "\n"
#     if "int main() {" not in res:
#         res += """
# int main() {
#     return 0;
# }
#     """
    return res


def dump_function(module: ast.FunctionDef) -> str:
    res = ""
    ret_type = dump_expr(module.returns)
    name = module.name
    args = dump_function_args(module.args)
    res += f"extern \"C\" {ret_type} {name}({args}) " + "{\n"
    dumped_body = dump_body(module.body, indent=True)
    res += dumped_body
    res += "}"
    return res


def dump_function_args(args: ast.arguments):
    args_list = []
    print(type(args))
    for arg in args.args:
        print(type(arg))
        arg_name = arg.arg
        arg_type = arg.annotation.id
        args_list.append(f"{arg_type} {arg_name}")
    return ', '.join(args_list)


def dump_body(module: List[ast.stmt], indent=True) -> str:
    res = ""
    body_dumpers = {
        ast.While: dump_while,
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


def dump_compare(module: ast.Compare) -> str:
    comp_signs = {
       ast.Eq: "==",
       ast.NotEq: "!=",
       ast.Lt: "<",
       ast.LtE: "<=",
       ast.Gt: ">",
       ast.GtE: ">="
    }
    left = dump_expr(module.left)
    op = module.ops[0]
    op_sign = comp_signs[type(op)]
    right = dump_expr(module.comparators[0])
    return f"{left} {op_sign} {right}"


def dump_expr(module: ast.Expression) -> str:
    res = ""
    expr_dumpers = {
        ast.AnnAssign: dump_ann_assign,
        ast.Assign: dump_assign,
        ast.Name: dump_name,
        ast.Constant: dump_constant,
        ast.BinOp: dump_bin_op,
        ast.BoolOp: dump_bool_op,
        ast.Return: dump_return,

        ast.Compare: dump_compare,
        ast.While: dump_while
    }
    expr_class = type(module)
    res = expr_dumpers[expr_class](module)
    return res


def dump_name(module: ast.Name) -> str:
    res = ""
    res = module.id
    return res


def dump_constant(module: ast.Constant) -> str:
    return f"{module.value}"


def dump_ann_assign(module: ast.AnnAssign) -> str:
    target = dump_expr(module.target)
    value = dump_expr(module.value)
    target_type = dump_expr(module.annotation)
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
    }
    op_sign = bin_op_signs[type(op)]
    return f"({left} {op_sign} {right})"


def dump_bool_op(module: ast.BoolOp) -> str:
    res = ""
    left = dump_expr(module.values[0])
    right = dump_expr(module.values[1])
    op = module.op
    bool_op_signs = {
        ast.And: "&&",
        ast.Or: "||"
    }
    op_sign = bool_op_signs[type(op)]
    return f"({left} {op_sign} {right})"


def dump_return(module: ast.Return) -> str:
    res = ""
    value = dump_expr(module.value)
    return f"return {value}"

