import ast


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
    return res


def dump_function(module: ast.FunctionDef) -> str:
    res = ""
    ret_type = dump_expr(module.returns)
    name = module.name
    res += f"{ret_type} {name}() " + "{\n"
    for elem in module.body:
        res += "\t" + dump_expr(elem) + ";\n"
    res += "}"
    return res


def dump_expr(module: ast.Expression) -> str:
    res = ""
    expr_dumpers = {
        ast.AnnAssign: dump_ann_assign,
        ast.Assign: dump_assign,
        ast.Name: dump_name,
        ast.Constant: dump_constant,
        ast.BinOp: dump_bin_op,
        ast.Return: dump_return
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


def dump_return(module: ast.Return) -> str:
    res = ""
    value = dump_expr(module.value)
    return f"return {value}"

